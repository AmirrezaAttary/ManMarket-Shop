from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from cart.cart import CartSession
from cart.models import CartModel
from shop.models import ProductColorInventory
from accounts.scripts import send_bulk_sms
from wallets.models import WalletTransaction
from .models import PaymentModel, PayemntStatusType, PayemntType
from .zarinpal_client import ZarinPalSandbox
from .gsmpay_client import GSMPay
from .refah_client import RefahClient
from order.models import OrderModel, OrderStatusType


class PaymentVerifyView(View):
    """
    تایید پرداخت از درگاه‌های مختلف:
    - زرین‌پال
    - GSMPay
    - رفاه (POST)
    """

    def post(self, request, *args, **kwargs):
        """
        مخصوص دریافت POST از درگاه رفاه
        """
        token = request.POST.get("Token")
        status = request.POST.get("status")
        order_id = request.POST.get("OrderId")

        if not token or not status or not order_id:
            messages.error(request, "اطلاعات تراکنش ناقص است.")
            return redirect(reverse_lazy("order:checkout"))

        payment_obj = get_object_or_404(PaymentModel, authority_id=token)
        order = getattr(payment_obj, "order", None)
        response = {}
        verify_success = False

        if payment_obj.payemnt_type != PayemntType.refah.value:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect(reverse_lazy("order:checkout"))

        # تایید تراکنش با RefahClient
        refah = RefahClient()
        # مقدار amount در RefahClient بر اساس داکیومنت *10 هست
        response = refah.verify_transaction(amount=float(payment_obj.amount) * 10, token=token)

        # بررسی موفقیت تراکنش
        if response and "data" in response and response["data"].get("code") == 0:
            verify_success = True
        elif response and response.get("code") == 0:
            verify_success = True

        return self._process_payment_result(request, payment_obj, order, verify_success, response)

    def get(self, request, *args, **kwargs):
        """
        مخصوص GET از سایر درگاه‌ها (زرین‌پال و GSMPay)
        """
        token = request.GET.get("token") or request.GET.get("Authority")
        status = request.GET.get("Status")  # فقط برای زرین‌پال

        if not token:
            messages.error(request, "توکن پرداخت یافت نشد.")
            return redirect(reverse_lazy("order:checkout"))

        payment_obj = get_object_or_404(PaymentModel, authority_id=token)
        order = getattr(payment_obj, "order", None)
        response = {}
        verify_success = False

        # ================= زرین پال =================
        if payment_obj.payemnt_type in [
            PayemntType.cart.value,
            PayemntType.wallet_cart.value,
            PayemntType.cart_home.value
        ]:
            zarinpal = ZarinPalSandbox()
            response = zarinpal.payment_verify(int(payment_obj.amount), token)
            if status == "OK" and response.get("data", {}).get("code") == 100:
                verify_success = True

        # ================= GSMPay =================
        elif payment_obj.payemnt_type == PayemntType.gsm_cart.value:
            gsmpay = GSMPay()
            response, status_code = gsmpay.verify_payment(
                token=token,
                invoice_reference=f"ORDER-{order.id}",
                invoice_amount=int(payment_obj.amount)
            )
            if status_code == 200 and response.get("data", {}).get("is_paid"):
                verify_success = True

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect(reverse_lazy("order:checkout"))

        return self._process_payment_result(request, payment_obj, order, verify_success, response)

    def _process_payment_result(self, request, payment_obj, order, verify_success, response):
        """
        پردازش نهایی بعد از تایید یا عدم تایید تراکنش
        """
        if verify_success:
            payment_obj.status = PayemntStatusType.success.value
            payment_obj.ref_id = response.get("data", {}).get("refId") or payment_obj.authority_id
            payment_obj.response_code = response.get("data", {}).get("code")
            payment_obj.response_json = response
            payment_obj.save()

            # ================= پردازش سفارش =================
            if order:
                order.status = OrderStatusType.awaiting.value
                order.save()

                # کاهش موجودی انبار
                for item in order.order_items.all():
                    try:
                        inventory = ProductColorInventory.objects.get(
                            product=item.product, color=item.color
                        )
                        inventory.stock = max(0, inventory.stock - item.quantity)
                        inventory.save()
                    except ProductColorInventory.DoesNotExist:
                        continue

                # پرداخت ترکیبی با کیف پول
                if payment_obj.payemnt_type == PayemntType.wallet_cart.value and payment_obj.wallet:
                    wallet = payment_obj.wallet
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=wallet.balance,
                        description=f"پرداخت جزئی از سفارش #{order.id}",
                        transaction_type='payment'
                    )
                    wallet.balance = 0
                    wallet.save()

                # پیامک به مشتری و مدیر
                send_bulk_sms(
                    message_text=f"مشتری گرامی، سفارش شما {order.order_number} با موفقیت ثبت شد.\nمـــن مـــارکـــت",
                    mobiles=[order.user.phone_number]
                )
                send_bulk_sms(
                    message_text="✅ سفارش جدید در من‌مارکت ثبت شد.",
                    mobiles=["09120983411"]
                )

                # پاکسازی سبد خرید
                cart = CartModel.objects.filter(user=order.user).first()
                if cart:
                    cart.cart_items.all().delete()
                    CartSession(request.session).clear()

                return redirect(reverse_lazy("order:completed"))

            # شارژ کیف پول
            if payment_obj.wallet:
                wallet = payment_obj.wallet
                wallet.balance += payment_obj.amount
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=payment_obj.amount,
                    description="شارژ کیف پول با پرداخت آنلاین",
                    transaction_type='charge'
                )
                return redirect(reverse_lazy("wallets:charge_success"))

        # ================= پرداخت ناموفق =================
        payment_obj.status = PayemntStatusType.failed.value
        payment_obj.response_json = response
        payment_obj.save()

        if order:
            order.status = OrderStatusType.failed.value
            order.save()
            send_bulk_sms(
                message_text=f"پرداخت سفارش {order.order_number} ناموفق بود.\nدر صورت کسر وجه، تا ۲۴ ساعت بازگشت می‌یابد.",
                mobiles=[order.user.phone_number]
            )
            return redirect(reverse_lazy("order:failed"))

        if payment_obj.wallet:
            return redirect(reverse_lazy("wallets:charge_failed"))

        messages.error(request, "پرداخت با خطا مواجه شد.")
        return redirect(reverse_lazy("order:checkout"))
