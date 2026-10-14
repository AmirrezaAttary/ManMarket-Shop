import logging

from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.utils.html import escape
from django.views.decorators.http import require_GET
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from app.order.models import OrderStatusType
from app.payment.models import PaymentModel, PayemntStatusType, PayemntType
from app.payment.saman_client import SamanGateway, toman_to_rial

logger = logging.getLogger(__name__)

SUCCESS_URL = "https://manmarket.ir/payment/successfull"
FAILED_URL = "https://manmarket.ir/payment/failed"

ALLOWED_TYPES = [
    PayemntType.cart.value,
    PayemntType.cart_home.value,
    PayemntType.wallet_cart.value,
]


@require_GET
def saman_redirect(request, token):
    """
    سامان فقط فرم POST می‌پذیرد. فرانت فقط به این آدرس هدایت می‌شود
    (window.location = payment_url) و این صفحه فرم را خودکار ارسال می‌کند.
    """
    if not PaymentModel.objects.filter(
        authority_id=token, status=PayemntStatusType.pending.value
    ).exists():
        raise Http404

    html = f"""<!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8">
<title>انتقال به درگاه پرداخت</title></head>
<body onload="document.getElementById('f').submit()">
<p>در حال انتقال به درگاه پرداخت...</p>
<form id="f" method="post" action="{escape(SamanGateway.page_url)}">
  <input type="hidden" name="Token" value="{escape(token)}">
  <noscript><button type="submit">ادامه</button></noscript>
</form></body></html>"""
    return HttpResponse(html)


def _fail(payment, order):
    payment.status = PayemntStatusType.failed.value
    payment.save()
    if order:
        order.status = OrderStatusType.failed.value
        order.save()
    return redirect(FAILED_URL)


def _find_inventory(item):
    """
    موجودی مربوط به آیتم سفارش را پیدا می‌کند، بدون نیاز به تغییر مدل‌ها:
    اول item.color_inventory، وگرنه مدلی که به محصول وصل است و فیلدهای color و stock دارد.
    """
    inventory = getattr(item, "color_inventory", None)
    if inventory is not None:
        return inventory
    for rel in item.product._meta.related_objects:
        model = rel.related_model
        names = {f.name for f in model._meta.get_fields()}
        if {"color", "stock"} <= names:
            found = model.objects.filter(
                **{rel.field.name: item.product, "color": item.color}
            ).first()
            if found:
                return found
    raise LookupError(f"inventory not found for order item {item.pk}")


def _locked_inventories(order):
    """موجودی هر آیتم را قفل می‌کند تا هم‌زمانی باعث منفی‌شدن موجودی نشود."""
    result = []
    for item in order.order_items.all():
        inventory = _find_inventory(item)
        inventory = type(inventory).objects.select_for_update().get(pk=inventory.pk)
        result.append((item, inventory))
    return result


class PaymentVerifyAPIView(APIView):
    """
    callback درگاه سامان. بانک کاربر را بدون توکن JWT برمی‌گرداند،
    پس احراز هویت/CSRF نباید اعمال شود؛ اعتبار درخواست با verify سمت بانک تضمین می‌شود.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return self._handle(request.data)

    def get(self, request, *args, **kwargs):
        return self._handle(request.query_params)

    def _handle(self, data):
        payload = data.dict() if hasattr(data, "dict") else dict(data)
        res_num = str(payload.get("ResNum", ""))
        ref_num = payload.get("RefNum")
        state = payload.get("State")

        if not res_num.isdigit():
            return redirect(FAILED_URL)

        with transaction.atomic():
            payment = (
                PaymentModel.objects.select_for_update()
                .filter(id=int(res_num))
                .first()
            )
            if not payment:
                return redirect(FAILED_URL)

            # callback تکراری یا پرداخت باطل‌شده نباید دوباره پردازش شود
            if payment.status != PayemntStatusType.pending.value:
                return redirect(FAILED_URL)
            if payment.payemnt_type not in ALLOWED_TYPES:
                return redirect(FAILED_URL)

            order = getattr(payment, "order", None)
            payment.response_json = {"callback": payload}
            payment.save()

            # انصراف کاربر یا پرداخت ناموفق
            if state != "OK" or not ref_num:
                return _fail(payment, order)

            # RefNum استفاده‌شده در پرداخت دیگر
            if PaymentModel.objects.filter(
                status=PayemntStatusType.success.value,
                response_json__callback__RefNum=ref_num,
            ).exists():
                return _fail(payment, order)

            # موجودی را قبل از verify بررسی می‌کنیم؛ اگر کافی نباشد verify نمی‌کنیم
            # و تراکنشِ تأییدنشده توسط بانک به‌صورت خودکار به مشتری برمی‌گردد.
            inventories = _locked_inventories(order) if order else []
            if any(inv.stock < item.quantity for item, inv in inventories):
                return _fail(payment, order)

            saman = SamanGateway()
            result = saman.payment_verify(ref_num)
            payment.response_json = {"callback": payload, "verify": result}
            payment.save()

            verified = result.get("Success") is True and result.get("ResultCode") == 0

            # مبلغ را از پاسخ «بانک» با مبلغ سفارش مقایسه می‌کنیم (نه از callback)
            if verified:
                info = result.get("VerifyInfo") or result.get("TransactionDetail") or {}
                paid = next(
                    (info[k] for k in ("OrginalAmount", "OriginalAmount", "Amount") if k in info),
                    None,
                )
                try:
                    amount_ok = paid is not None and int(paid) == toman_to_rial(payment.amount)
                except (TypeError, ValueError):
                    amount_ok = False

                if not amount_ok:
                    logger.error("Saman amount mismatch/missing for payment %s: %s", payment.id, result)
                    reverse = saman.payment_reverse(ref_num)
                    payment.response_json = {
                        "callback": payload, "verify": result, "reverse": reverse
                    }
                    return _fail(payment, order)
            else:
                return _fail(payment, order)

            # موفق
            rrn = payload.get("RRN") or payload.get("Rrn")
            payment.status = PayemntStatusType.success.value
            payment.ref_id = int(rrn) if rrn and str(rrn).isdigit() else None
            payment.response_code = 0
            payment.save()

            if order:
                order.status = OrderStatusType.awaiting.value
                order.save()
                for item, inv in inventories:
                    inv.stock -= item.quantity
                    inv.save()

        return redirect(SUCCESS_URL)