import logging
import re
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from app.cart.models import CartModel
from app.order.models import OrderItemModel, OrderModel, OrderStatusType
from app.shop.models import ProductColorInventory
from app.shop.models.products import ProductStatusType

from .client import BWDKClient, BWDKError
from .models import BWDKOrder, BWDKOrderStatus

log = logging.getLogger("bwdk")
User = get_user_model()

VERIFY_RETRY_AFTER = timedelta(minutes=20)  # doc: retry Verify ~20 min after a failed attempt
PHONE_RE = re.compile(r"^09\d{9}$")


def normalize_phone(raw):
    """'+989121234567' / '989121234567' / '9121234567' / '09121234567' -> '09121234567'"""
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("0098"):
        digits = digits[4:]
    elif digits.startswith("98"):
        digits = digits[2:]
    digits = digits.lstrip("0")
    return f"0{digits}" if digits else ""


def _cut(value, size):
    return (value or "")[:size]


class BWDKService:
    """Maps ManMarket carts/orders to Digikala BWDK (create -> callback -> Get -> Verify)."""

    def __init__(self):
        self.client = BWDKClient()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def guest_owner():
        """Placeholder owner for orders created without login (doc: 'temp user' approach).
        It can never log in; the real owner is attached after payment from the phone number."""
        phone = getattr(settings, "BWDK_GUEST_PHONE", "09000000000")
        user, created = User.objects.get_or_create(
            phone_number=phone, defaults={"is_active": False, "is_verified": False}
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        return user

    @staticmethod
    def _absolute_image_url(request, image):
        if not image:
            return ""
        try:
            return request.build_absolute_uri(image.url)
        except (AttributeError, ValueError):
            return ""

    # ------------------------------------------------------------------- create
    def _collect_lines(self, user, items):
        """Returns {inventory_id: quantity}. Logged-in users without `items` use their DB cart."""
        wanted = {}
        if items:
            for entry in items:
                inv_id, qty = int(entry["color_inventory"]), int(entry["quantity"])
                wanted[inv_id] = wanted.get(inv_id, 0) + qty
        elif user is not None and user.is_authenticated:
            cart = CartModel.objects.filter(user=user).first()
            if cart:
                for ci in cart.cart_items.all():
                    wanted[ci.color_inventory_id] = wanted.get(ci.color_inventory_id, 0) + ci.quantity
        if not wanted:
            raise ValueError("سبد خرید شما خالی است.")
        return wanted

    @transaction.atomic
    def create_checkout(self, *, user, items, request):
        is_guest = user is None or not user.is_authenticated
        wanted = self._collect_lines(user, items)

        # lock the inventory rows: the stock is RESERVED for the payment window
        inventories = {
            inv.pk: inv
            for inv in ProductColorInventory.objects.select_for_update()
            .select_related("product", "color")
            .filter(pk__in=wanted.keys())
        }
        if len(inventories) != len(wanted):
            raise ValueError("بعضی از کالاهای سبد خرید دیگر موجود نیستند.")

        for inv_id, qty in wanted.items():
            inv = inventories[inv_id]
            if inv.product.status != ProductStatusType.publish.value:
                raise ValueError(f"محصول «{inv.product.title}» در حال حاضر قابل سفارش نیست.")
            if qty < 1 or inv.get_price() <= 0 or inv.stock < qty:
                raise ValueError(f"موجودی محصول «{inv.product.title}» کافی نیست.")

        owner = self.guest_owner() if is_guest else user
        order = OrderModel.objects.create(
            user=owner,
            name="" if is_guest else (getattr(owner, "get_full_name", lambda: "")() or str(owner)),
            phone_number="" if is_guest else (owner.phone_number or ""),
            address="",
            state="",
            city="",
            zip_code="",
            total_price=0,
            status=OrderStatusType.pending.value,
        )

        payload_items, main_amount, total_weight = [], 0, 0
        item_weight = int(getattr(settings, "BWDK_DEFAULT_ITEM_WEIGHT", 0))
        prep_time = int(getattr(settings, "BWDK_DEFAULT_PREPARATION_TIME", 1))

        for inv_id, qty in wanted.items():
            inv = inventories[inv_id]
            unit_price = int(inv.get_price())
            primary_price = max(int(inv.get_price_product()), unit_price)

            OrderItemModel.objects.create(
                order=order, product=inv.product, color=inv.color, quantity=qty, price=unit_price
            )
            # reserve: decrement now, give back if the order is cancelled / expires
            ProductColorInventory.objects.filter(pk=inv.pk).update(stock=models.F("stock") - qty)

            main_amount += unit_price * qty
            total_weight += item_weight * qty
            payload_items.append(
                {
                    "id": inv.pk,  # variant id = ProductColorInventory id
                    "name": inv.product.title,
                    "primary_amount": primary_price,
                    "amount": unit_price,
                    "count": qty,
                    # item discount is for coupon-like discounts ONLY, never (primary - amount)
                    "discount_amount": 0,
                    "tax_amount": 0,
                    "image_link": self._absolute_image_url(request, inv.product.image),
                    "preparation_time": prep_time,
                    **({"weight": item_weight} if item_weight else {}),
                    "has_tax": False,
                    "tax_percent": 0,
                    "options": [
                        {
                            "type_name": "color",
                            "name": inv.color.title,
                            "value": inv.hex_color or inv.color.hex_color or "#000000",
                            "is_color": True,
                        }
                    ],
                }
            )

        order.total_price = Decimal(main_amount)
        order.save(update_fields=["total_price", "updated_date"])

        reservation_minutes = max(int(getattr(settings, "BWDK_RESERVATION_MINUTES", 30)), 25)
        expires_at = timezone.now() + timedelta(minutes=reservation_minutes)
        merchant_unique_id = f"mm-{order.id}-{uuid4().hex}"
        merchant_order_id = str(order.order_number)
        callback_base = getattr(settings, "BWDK_CALLBACK_BASE", "https://manmarket.ir").rstrip("/")

        bw = BWDKOrder.objects.create(
            order=order,
            merchant_unique_id=merchant_unique_id,
            merchant_order_id=merchant_order_id,
            main_amount=main_amount,
            final_amount=main_amount,
            guest_checkout=is_guest,
            stock_reserved=True,
            reservation_expires_at=expires_at,
        )

        payload = {
            "merchant_unique_id": merchant_unique_id,
            "merchant_order_id": merchant_order_id,
            "main_amount": main_amount,
            "discount_amount": 0,
            "loyalty_amount": 0,
            "tax_amount": 0,
            "final_amount": main_amount,
            # No query string allowed. The callback page lives on the registered (front) domain and
            # finds the order by the id in the PATH.
            "callback_url": f"{callback_base}/bwdk/callback/{merchant_unique_id}/",
            "reservation_expired_at": int(expires_at.timestamp()),
            "preparation_time": prep_time,
            "items": payload_items,
        }
        if total_weight:
            payload["weight"] = total_weight

        try:
            data = self.client.create_order(payload)
        except BWDKError as exc:
            log.error("BWDK create-order failed: %s | %s", exc, exc.payload)
            # raising inside atomic() rolls back the order AND the stock reservation
            raise ValueError("اتصال به سرویس خرید با دیجی‌کالا برقرار نشد. لطفاً دوباره تلاش کنید.") from exc

        if not data.get("order_uuid") or not data.get("order_start_url"):
            log.error("BWDK create-order unexpected answer: %s", data)
            raise ValueError("پاسخ نامعتبر از سرویس خرید با دیجی‌کالا دریافت شد.")

        bw.order_uuid = data["order_uuid"]
        bw.order_start_url = data["order_start_url"]
        bw.status = BWDKOrderStatus.PENDING
        bw.status_display = BWDKOrderStatus.PENDING.label
        bw.last_response = data
        bw.save()
        return bw

    # --------------------------------------------------- callback / reconcile
    def complete(self, merchant_unique_id, edit_basket=False):
        """Called by the Next.js callback page. Query-string values are NEVER trusted: the state
        always comes from Get Order. Idempotent - safe to call repeatedly (polling)."""
        with transaction.atomic():
            bw = BWDKOrder.objects.select_for_update().select_related("order").get(
                merchant_unique_id=merchant_unique_id
            )
            self._reconcile_locked(bw, edit_basket=edit_basket)
        return self.result_for(bw, edit_basket)

    def reconcile(self, bw_id):
        """Same as complete() but for cron / admin."""
        with transaction.atomic():
            bw = BWDKOrder.objects.select_for_update().select_related("order").get(pk=bw_id)
            self._reconcile_locked(bw)
        return bw

    def _reconcile_locked(self, bw, edit_basket=False):
        if not bw.order_uuid:
            return bw
        if bw.finalized_at and bw.status in (
            BWDKOrderStatus.VERIFIED_BY_MERCHANT,
            BWDKOrderStatus.REFUND_COMPLETED,
            BWDKOrderStatus.SHIPPED,
            BWDKOrderStatus.DELIVERED,
        ):
            return bw

        try:
            remote = self.client.get_order(bw.order_uuid)
        except BWDKError as exc:
            log.warning("BWDK get-order failed (bwdk #%s): %s", bw.pk, exc)
            return bw

        self._store_remote(bw, remote)
        status = int(remote.get("status") or 0)

        if status == BWDKOrderStatus.PAID_BY_USER:
            self._verify_and_finalize(bw, remote)
        elif status == BWDKOrderStatus.VERIFIED_BY_MERCHANT:
            self._finalize_locally(bw, remote)  # verified earlier, shop side not finished yet
        elif bw.is_open and (
            status in (
                BWDKOrderStatus.PENDING,
                BWDKOrderStatus.EXPIRED,
                BWDKOrderStatus.FAILED_TO_PAY,
                BWDKOrderStatus.RESERVATION_EXPIRED,
            )
            or (edit_basket and status != BWDKOrderStatus.WAITING_FOR_GATEWAY)
        ):
            self._cancel_locally(bw, f"bwdk status {status}" + (" (edit basket)" if edit_basket else ""))
        return bw

    def _store_remote(self, bw, remote):
        """Stores what BWDK says. main/final/discount/tax are OUR amounts and are kept untouched
        so they can be cross-checked before Verify."""
        bw.status = int(remote.get("status") or bw.status)
        bw.status_display = remote.get("status_display", "") or bw.status_display
        bw.reference_code = remote.get("reference_code", "") or bw.reference_code
        bw.total_paid_amount = remote.get("total_paid_amount") or 0
        bw.promotion_discount_amount = remote.get("promotion_discount_amount") or 0
        bw.shipping_amount = remote.get("shipping_amount") or 0
        bw.packing_amount = remote.get("packing_amount") or 0
        bw.digipay_markup_amount = remote.get("digipay_markup_amount") or 0
        bw.payment_data = remote.get("payment") or {}
        bw.destination_address = remote.get("destination_address") or {}
        bw.shipping_data = remote.get("selected_shipping_method") or {}
        bw.customer_data = remote.get("user") or {}
        bw.items_data = remote.get("items") or []
        bw.last_response = remote
        bw.last_synced_at = timezone.now()
        if remote.get("created_at"):
            bw.created_at_bwdk = parse_datetime(remote["created_at"])
        if (remote.get("payment") or {}).get("paid_at"):
            bw.paid_at = parse_datetime(remote["payment"]["paid_at"])
        bw.save()

    @staticmethod
    def _integrity_problem(bw, remote):
        """Cross-check what BWDK holds against what we sent. Returns a text, or None if all fine."""
        problems = []
        checks = {
            "merchant_order_id": (str(remote.get("merchant_order_id")), str(bw.merchant_order_id)),
            "main_amount": (int(remote.get("main_amount") or 0), int(bw.main_amount)),
            "discount_amount": (int(remote.get("discount_amount") or 0), int(bw.discount_amount)),
            "tax_amount": (int(remote.get("tax_amount") or 0), int(bw.tax_amount)),
        }
        for key, (got, ours) in checks.items():
            if got != ours:
                problems.append(f"{key}: bwdk={got} shop={ours}")

        # Get Order does not return our variant id, and names may be re-written by Digify, so the
        # lines are compared by (count, unit price) only.
        remote_items = sorted((int(i.get("count") or 0), int(i.get("amount") or 0)) for i in remote.get("items", []))
        local_items = sorted((oi.quantity, int(oi.price)) for oi in bw.order.order_items.all())
        if remote_items != local_items:
            problems.append("items differ between BWDK and the shop order")

        if not remote.get("is_paid") or int(remote.get("total_paid_amount") or 0) <= 0:
            problems.append("not paid according to Get Order")
        return "; ".join(problems) or None

    def _verify_and_finalize(self, bw, remote):
        problem = self._integrity_problem(bw, remote)
        if problem:
            bw.needs_review = True
            bw.review_note = f"Mismatch before Verify -> {problem}"
            bw.save(update_fields=["needs_review", "review_note", "updated_date"])
            log.error("BWDK integrity problem (bwdk #%s): %s", bw.pk, problem)
            return

        bw.verify_attempts += 1
        bw.last_verify_attempt_at = timezone.now()
        try:
            verify_data = self.client.verify_order(bw.order_uuid, bw.merchant_unique_id)
        except BWDKError as exc:
            log.warning("BWDK verify failed (bwdk #%s): %s | %s", bw.pk, exc, exc.payload)
            bw.last_response = exc.payload or {"error": str(exc)}
            bw.save(update_fields=["verify_attempts", "last_verify_attempt_at", "last_response", "updated_date"])
            return  # cron retries ~20 min later; Get Order is always checked first

        bw.last_response = verify_data
        bw.verified_at = timezone.now()
        bw.status = BWDKOrderStatus.VERIFIED_BY_MERCHANT
        bw.status_display = BWDKOrderStatus.VERIFIED_BY_MERCHANT.label
        bw.save()
        self._finalize_locally(bw, remote)

    def _resolve_user(self, bw, remote):
        order = bw.order
        if not bw.guest_checkout:
            return order.user  # logged-in buyer keeps the order

        phone = normalize_phone((remote.get("user") or {}).get("phone_number", ""))
        if not PHONE_RE.match(phone):
            bw.needs_review = True
            bw.review_note = (bw.review_note + "\n" if bw.review_note else "") + (
                f"شماره موبایل مشتری معتبر نیست ({phone or '-'}); سفارش روی کاربر موقت مانده است."
            )
            bw.save(update_fields=["needs_review", "review_note", "updated_date"])
            return order.user

        user, created = User.objects.get_or_create(
            phone_number=phone, defaults={"is_active": True, "is_verified": False}
        )
        profile = getattr(user, "user_profile", None)
        data = remote.get("user") or {}
        if profile:
            changed = False
            if not profile.first_name and data.get("first_name"):
                profile.first_name, changed = _cut(data["first_name"], 255), True
            if not profile.last_name and data.get("last_name"):
                profile.last_name, changed = _cut(data["last_name"], 255), True
            if changed:
                profile.save(update_fields=["first_name", "last_name", "updated_date"])
        return user

    def _finalize_locally(self, bw, remote):
        if bw.finalized_at:
            return
        if bw.cancelled_at:  # paid after we released the stock -> a human must decide
            bw.needs_review = True
            bw.review_note = "پرداخت بعد از لغو سفارش و آزادسازی موجودی انجام شده است؛ بررسی دستی لازم است."
            bw.save(update_fields=["needs_review", "review_note", "updated_date"])
            return

        order = bw.order
        user = self._resolve_user(bw, remote)
        dest = remote.get("destination_address") or {}

        extra = []
        if dest.get("building_number"):
            extra.append(f"پلاک {dest['building_number']}")
        if dest.get("unit"):
            extra.append(f"واحد {dest['unit']}")
        if dest.get("district_name"):
            extra.append(f"منطقه {dest['district_name']}")
        address = "، ".join(filter(None, [dest.get("address"), *extra]))

        order.user = user
        order.name = _cut(dest.get("receiver_name") or order.name, 250)
        order.phone_number = _cut(normalize_phone(dest.get("receiver_phone") or "") or user.phone_number, 250)
        order.address = _cut(address, 250)
        order.state = _cut(dest.get("state_name"), 50)
        order.city = _cut(dest.get("city_name"), 50)
        order.zip_code = _cut(dest.get("postal_code"), 50)
        order.status = OrderStatusType.success.value  # paid + verified -> "در حال پردازش"
        order.save()

        # stock was reserved at create time: only the sales counter is left
        from app.shop.models.products import ProductModel

        for item in order.order_items.all():
            ProductModel.objects.filter(pk=item.product_id).update(
                sales_count=models.F("sales_count") + item.quantity
            )

        # remove only the purchased lines from the buyer's saved cart
        cart = CartModel.objects.filter(user=user).first()
        if cart:
            for item in order.order_items.all():
                cart.cart_items.filter(product_id=item.product_id, color_id=item.color_id).delete()

        bw.stock_reserved = False
        bw.finalized_at = timezone.now()
        bw.save(update_fields=["stock_reserved", "finalized_at", "updated_date"])

    def _restock(self, bw):
        if not bw.stock_reserved:
            return
        for item in bw.order.order_items.all():
            ProductColorInventory.objects.filter(product_id=item.product_id, color_id=item.color_id).update(
                stock=models.F("stock") + item.quantity
            )
        bw.stock_reserved = False

    def _cancel_locally(self, bw, reason):
        self._restock(bw)
        order = bw.order
        if order.status == OrderStatusType.pending.value:
            order.status = OrderStatusType.failed.value
            order.save(update_fields=["status", "updated_date"])
        bw.cancelled_at = timezone.now()
        bw.save(update_fields=["stock_reserved", "cancelled_at", "updated_date"])
        log.info("BWDK order #%s cancelled locally: %s", bw.pk, reason)

    @staticmethod
    def result_for(bw, edit_basket=False):
        if bw.finalized_at:
            state = "paid"
        elif bw.needs_review:
            state = "review"
        elif bw.cancelled_at:
            state = "edit_basket" if edit_basket else "failed"
        else:
            state = "pending"  # Verify not finished yet - the front polls
        return {
            "state": state,
            "order_id": bw.order_id,
            "order_number": bw.merchant_order_id,
            "reference_code": bw.reference_code,
            "status": bw.status,
        }

    # --------------------------------------------------------------------- cron
    def sync_open_orders(self):
        """
        * Verify failed before      -> 20 minutes later: Get Order, Verify again if status == 7
        * user never came back      -> when the reservation is over: Get Order, cancel + restock
                                       only if BWDK confirms it was not paid
        """
        now = timezone.now()
        due = models.Q(last_verify_attempt_at__lte=now - VERIFY_RETRY_AFTER) | models.Q(
            last_verify_attempt_at__isnull=True, reservation_expires_at__lte=now
        )
        qs = BWDKOrder.objects.filter(
            due,
            finalized_at__isnull=True,
            cancelled_at__isnull=True,
            order_uuid__isnull=False,
            needs_review=False,
            created_date__gte=now - timedelta(days=3),
        )
        done = 0
        for bw_id in qs.values_list("pk", flat=True):
            try:
                self.reconcile(bw_id)
                done += 1
            except Exception:  # one broken order must not block the others
                log.exception("BWDK sync failed for #%s", bw_id)
        return done

    # ------------------------------------------------------------ admin actions
    def manual_verify(self, bw):
        """Panel button 'Verify سفارش': Get Order first, Verify only when status == 7."""
        return self.reconcile(bw.pk)

    def refund(self, bw, reason):
        """Full refund only (the API supports nothing else) and only for Digipay payments."""
        with transaction.atomic():
            bw = BWDKOrder.objects.select_for_update().select_related("order").get(pk=bw.pk)
            try:
                remote = self.client.get_order(bw.order_uuid)
            except BWDKError as exc:
                raise ValueError(exc.detail) from exc
            self._store_remote(bw, remote)

            if (remote.get("payment") or {}).get("gateway_name") != "Digipay":
                raise ValueError("بازگشت وجه فقط برای سفارش‌های پرداخت‌شده با دیجی‌پی از این مسیر ممکن است.")
            if bw.status == BWDKOrderStatus.REFUND_COMPLETED:
                raise ValueError("این سفارش قبلاً مرجوع شده است.")

            amount = int(remote.get("total_paid_amount") or 0)
            try:
                data = self.client.refund_order(bw.order_uuid, reason, amount)
            except BWDKError as exc:
                # e.g. 400 when the money was already settled with the merchant
                raise ValueError(exc.detail or "درخواست بازگشت وجه پذیرفته نشد.") from exc

            bw.last_response = data
            bw.status = BWDKOrderStatus.REFUND_COMPLETED
            bw.status_display = BWDKOrderStatus.REFUND_COMPLETED.label
            bw.save()

            order = bw.order
            if order.status in (OrderStatusType.awaiting.value, OrderStatusType.success.value):
                # not shipped yet: give the goods back to the shelf
                for item in order.order_items.all():
                    ProductColorInventory.objects.filter(
                        product_id=item.product_id, color_id=item.color_id
                    ).update(stock=models.F("stock") + item.quantity)
            order.status = OrderStatusType.failed.value
            order.save(update_fields=["status", "updated_date"])
        return bw
