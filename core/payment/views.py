from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
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

# =========================================
# ویو عمومی برای سایر درگاه‌ها
# =========================================
class PaymentVerifyView(View):
    """
    تایید پرداخت آنلاین: زرین‌پال و GSMPay
    """
    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority") or request.GET.get("token")
        status = request.GET.get("Status")
        payment_obj = get_object_or_404(PaymentModel, authority_id=authority_id)

        order = getattr(payment_obj, "order", None)
        response = {}
        is_success = False

        # ---------------- زرین‌پال ----------------
        if payment_obj.payemnt_type in [PayemntType.cart.value, PayemntType.wallet_cart.value, PayemntType.cart_home.value]:
            zarin_pal = ZarinPalSandbox()
            response = zarin_pal.payment_verify(int(payment_obj.amount), payment_obj.authority_id)
            if status == "OK" and response.get("data", {}).get("code") == 100:
                is_success = True

        # ---------------- GSMPay ----------------
        elif payment_obj.payemnt_type == PayemntType.gsm_cart.value:
            gsmpay = GSMPay()
            response, status_code = gsmpay.verify_payment(
                token=payment_obj.authority_id,
                invoice_reference=f"ORDER-{order.id}",
                invoice_amount=int(payment_obj.amount)
            )
            if status_code == 200 and response.get("data", {}).get("is_paid"):
                is_success = True

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect(reverse_lazy("order:checkout"))

        return self.process_payment_result(request, payment_obj, order, is_success, response)

    def process_payment_result(self, request, payment_obj, order, is_success, response):
        """
        پردازش نتیجه پرداخت برای همه درگاه‌ها
        """
        if is_success:
            payment_obj.status = PayemntStatusType.success.value
            payment_obj.ref_id = response.get("data", {}).get("refId") or payment_obj.authority_id
            payment_obj.response_code = response.get("data", {}).get("code")
            payment_obj.response_json = response
            payment_obj.save()

            if order:
                order.status = OrderStatusType.awaiting.value
                order.save()

                # کاهش موجودی انبار
                for item in order.order_items.all():
                    try:
                        inventory = ProductColorInventory.objects.get(product=item.product, color=item.color)
                        inventory.stock = max(0, inventory.stock - item.quantity)
                        inventory.save()
                    except ProductColorInventory.DoesNotExist:
                        continue

                # پرداخت ترکیبی کیف پول
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

                # ارسال پیامک
                send_bulk_sms(f"سفارش شما {order.order_number} ثبت شد.", [order.user.phone_number])
                send_bulk_sms("سفارش جدید در من‌مارکت ثبت شد.", ["09120983411"])

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
                    description="شارژ کیف پول از طریق پرداخت آنلاین",
                    transaction_type='charge'
                )
                return redirect(reverse_lazy("wallets:charge_success"))

        # ---------------- پرداخت ناموفق ----------------
        payment_obj.status = PayemntStatusType.failed.value
        payment_obj.response_json = response
        payment_obj.save()

        if order:
            order.status = OrderStatusType.failed.value
            order.save()
            send_bulk_sms(f"پرداخت سفارش {order.order_number} ناموفق بود.", [order.user.phone_number])
            return redirect(reverse_lazy("order:failed"))

        if payment_obj.wallet:
            return redirect(reverse_lazy("wallets:charge_failed"))

        messages.error(request, "پرداخت با خطا مواجه شد.")
        return redirect(reverse_lazy("order:checkout"))


# =========================================
# ویو مخصوص رفاه
# =========================================
@method_decorator(csrf_exempt, name='dispatch')
class RefahCallbackView(View):
    """
    دریافت POST از درگاه رفاه و تایید تراکنش
    """

    def post(self, request, *args, **kwargs):
        token = request.POST.get("Token")
        status = request.POST.get("status")  # 0 = موفق
        order_id = request.POST.get("OrderId")

        if not token:
            messages.error(request, "توکن پرداخت یافت نشد.")
            return redirect(reverse_lazy("order:checkout"))

        payment_obj = get_object_or_404(PaymentModel, authority_id=token)
        order = getattr(payment_obj, "order", None)

        refah = RefahClient()
        response = refah.verify_transaction(amount=payment_obj.amount*10, token=token)

        # بررسی موفقیت
        is_success = False
        if response and "data" in response and int(response["data"].get("code", -1)) == 0:
            is_success = True
        elif response and int(response.get("code", -1)) == 0:
            is_success = True

        # پردازش نتیجه مشابه سایر درگاه‌ها
        return PaymentVerifyView().process_payment_result(request, payment_obj, order, is_success, response)
