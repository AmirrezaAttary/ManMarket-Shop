from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
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


@method_decorator(csrf_exempt, name='dispatch')
class PaymentVerifyView(View):
    """
    تایید پرداخت از درگاه‌های مختلف (زرین‌پال، GSMPay، رفاه)
    """

    def dispatch(self, *args, **kwargs):
        """غیرفعال کردن CSRF برای درگاه رفاه"""
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """تایید برای زرین‌پال و GSMPay (بازگشت با GET)"""
        return self._verify_common(request, method="GET")

    def post(self, request, *args, **kwargs):
        """تایید برای درگاه رفاه (بازگشت با POST)"""
        return self._verify_common(request, method="POST")

    def _verify_common(self, request, method="GET"):
        response = {}
        verify_success = False
        payment_obj = None
        order = None

        try:
            if method == "POST" and "Token" in request.POST:
                # ===== درگاه رفاه =====
                token = request.POST.get("Token")
                status = request.POST.get("status")
                order_id = request.POST.get("OrderId")
                rrn = request.POST.get("RRN")
                amount = request.POST.get("Amount")

                order = get_object_or_404(OrderModel, id=order_id)
                payment_obj = order.payment

                # اگر کاربر پرداخت را لغو کرده باشد
                if status != "0":
                    payment_obj.status = PayemntStatusType.failed.value
                    payment_obj.save()
                    messages.error(request, "پرداخت توسط کاربر لغو شد.")
                    return redirect(reverse_lazy("order:failed"))

                # تأیید تراکنش رفاه
                refah = RefahClient()
                response = refah.verify_transaction(amount=float(amount), token=token)
                if response and response.get("responseCode") == 0:
                    verify_success = True
                elif "data" in response and response["data"].get("code") == 0:
                    verify_success = True

            else:
                # ===== درگاه زرین‌پال یا GSMPay =====
                token = request.GET.get("token") or request.GET.get("Authority")
                status = request.GET.get("Status")
                payment_obj = get_object_or_404(PaymentModel, authority_id=token)
                order = getattr(payment_obj, "order", None)

                if payment_obj.payemnt_type in [
                    PayemntType.cart.value,
                    PayemntType.wallet_cart.value,
                    PayemntType.cart_home.value,
                ]:
                    zarinpal = ZarinPalSandbox()
                    response = zarinpal.payment_verify(int(payment_obj.amount), token)
                    if status == "OK" and response.get("data", {}).get("code") == 100:
                        verify_success = True

                elif payment_obj.payemnt_type == PayemntType.gsm_cart.value:
                    gsmpay = GSMPay()
                    response, status_code = gsmpay.verify_payment(
                        token=token,
                        invoice_reference=f"ORDER-{order.id}",
                        invoice_amount=int(payment_obj.amount),
                    )
                    if status_code == 200 and response.get("data", {}).get("is_paid"):
                        verify_success = True

            # ======= نتیجه موفق =======
            if verify_success and payment_obj:
                payment_obj.status = PayemntStatusType.success.value
                payment_obj.ref_id = (
                    response.get("data", {}).get("refId")
                    or response.get("RRN")
                    or payment_obj.authority_id
                )
                payment_obj.response_code = (
                    response.get("responseCode")
                    or response.get("data", {}).get("code")
                )
                payment_obj.response_json = response
                payment_obj.save()

                # در صورت داشتن سفارش
                if order:
                    order.status = OrderStatusType.awaiting.value
                    order.save()

                    # کاهش موجودی
                    for item in order.order_items.all():
                        try:
                            inventory = ProductColorInventory.objects.get(
                                product=item.product, color=item.color
                            )
                            inventory.stock = max(0, inventory.stock - item.quantity)
                            inventory.save()
                        except ProductColorInventory.DoesNotExist:
                            continue

                    # پرداخت ترکیبی
                    if (
                        payment_obj.payemnt_type == PayemntType.wallet_cart.value
                        and payment_obj.wallet
                    ):
                        wallet = payment_obj.wallet
                        WalletTransaction.objects.create(
                            wallet=wallet,
                            amount=wallet.balance,
                            description=f"پرداخت جزئی از سفارش #{order.id}",
                            transaction_type="payment",
                        )
                        wallet.balance = 0
                        wallet.save()

                    # پیامک‌ها
                    send_bulk_sms(
                        message_text=f"مشتری گرامی، سفارش شما {order.order_number} با موفقیت ثبت شد.\nمـــن مـــارکـــت",
                        mobiles=[order.user.phone_number],
                    )
                    send_bulk_sms(
                        message_text="✅ سفارش جدید در من‌مارکت ثبت شد.",
                        mobiles=["09120983411"],
                    )

                    # پاکسازی سبد
                    cart = CartModel.objects.filter(user=order.user).first()
                    if cart:
                        cart.cart_items.all().delete()
                        CartSession(request.session).clear()

                    return redirect(reverse_lazy("order:completed"))

                # در صورت شارژ کیف پول
                if payment_obj.wallet:
                    wallet = payment_obj.wallet
                    wallet.balance += payment_obj.amount
                    wallet.save()
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=payment_obj.amount,
                        description="شارژ کیف پول با پرداخت آنلاین",
                        transaction_type="charge",
                    )
                    return redirect(reverse_lazy("wallets:charge_success"))

            # ======= ناموفق =======
            if payment_obj:
                payment_obj.status = PayemntStatusType.failed.value
                payment_obj.response_json = response
                payment_obj.save()

            if order:
                order.status = OrderStatusType.failed.value
                order.save()
                send_bulk_sms(
                    message_text=f"پرداخت سفارش {order.order_number} ناموفق بود.\nدر صورت کسر وجه، تا ۲۴ ساعت بازگشت می‌یابد.",
                    mobiles=[order.user.phone_number],
                )
                return redirect(reverse_lazy("order:failed"))

            if payment_obj and payment_obj.wallet:
                return redirect(reverse_lazy("wallets:charge_failed"))

            messages.error(request, "پرداخت با خطا مواجه شد.")
            return redirect(reverse_lazy("order:checkout"))

        except Exception as e:
            print("Payment verify error:", e)
            messages.error(request, f"خطا در تایید پرداخت: {str(e)}")
            return redirect(reverse_lazy("order:checkout"))
