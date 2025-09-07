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
from order.models import OrderModel, OrderStatusType


class PaymentVerifyView(View):
    """
    تایید پرداخت آنلاین: زرین‌پال و GSMPay
    """

    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority") or request.GET.get("token")
        status = request.GET.get("Status")

        payment_obj = get_object_or_404(PaymentModel, authority_id=authority_id)

        # 🔹 بررسی نوع درگاه
        if payment_obj.payemnt_type in [PayemntType.cart.value, PayemntType.wallet_cart.value, PayemntType.cart_home.value]:
            zarin_pal = ZarinPalSandbox()
            response = zarin_pal.payment_verify(int(payment_obj.amount), payment_obj.authority_id)
        elif payment_obj.payemnt_type == PayemntType.gsm_cart.value:
            gsmpay = GSMPay()
            response, status_code = gsmpay.verify_payment(
                token=payment_obj.authority_id,
                invoice_reference=f"ORDER-{payment_obj.order.id}",
                invoice_amount=int(payment_obj.amount)
            )
        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect(reverse_lazy("order:checkout"))

        # 🔹 پردازش موفقیت یا شکست پرداخت
        is_success = False
        if payment_obj.payemnt_type == PayemntType.gsm_cart.value:
            if status_code == 200 and response.get("data", {}).get("is_paid"):
                is_success = True
        else:
            if status == "OK" and response.get("data"):
                is_success = True

        if is_success:
            payment_obj.status = PayemntStatusType.success.value
            payment_obj.ref_id = response.get("data", {}).get("ref_id") or payment_obj.authority_id
            payment_obj.response_code = response.get("data", {}).get("code")
            payment_obj.response_json = response
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order:
                order.status = OrderStatusType.awaiting.value
                order.save()

                # کاهش موجودی محصولات
                for item in order.order_items.all():
                    try:
                        inventory = ProductColorInventory.objects.get(
                            product=item.product,
                            color=item.color
                        )
                        if inventory.stock >= item.quantity:
                            inventory.stock -= item.quantity
                            inventory.save()
                        else:
                            messages.error(
                                request,
                                f"موجودی محصول '{item.product.title}' کافی نیست. سفارش لغو شد."
                            )
                            order.status = OrderStatusType.failed.value
                            order.save()
                            payment_obj.status = PayemntStatusType.failed.value
                            payment_obj.save()
                            return redirect(reverse_lazy("order:failed"))
                    except ProductColorInventory.DoesNotExist:
                        continue

                # پردازش پرداخت ترکیبی کیف پول
                if payment_obj.payemnt_type == PayemntType.wallet_cart.value:
                    wallet = payment_obj.wallet
                    if wallet:
                        WalletTransaction.objects.create(
                            wallet=wallet,
                            amount=wallet.balance,
                            description=f"پرداخت جزئی از سفارش #{order.id}",
                            transaction_type='payment'
                        )
                        wallet.balance = 0
                        wallet.save()

                # پیامک مشتری و مدیر
                send_bulk_sms(
                    message_text=f"مشتری گرامی،\nسفارش شما {order.order_number} تأیید شد.\nدر حال آماده‌سازی است.\nمـــن مـــارکـــت",
                    mobiles=[f"{order.user.phone_number}"]
                )
                send_bulk_sms(
                    message_text="یک سفارش جدید در من مارکت ثبت شد !",
                    mobiles=["09120983411"]
                )

                # پاکسازی سبد خرید
                cart = CartModel.objects.filter(user=order.user).first()
                if cart:
                    cart.cart_items.all().delete()
                    CartSession(request.session).clear()

                return redirect(reverse_lazy("order:completed"))

            # پردازش شارژ کیف پول
            wallet = getattr(payment_obj, "wallet", None)
            if wallet:
                wallet.balance += payment_obj.amount
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=payment_obj.amount,
                    description="شارژ کیف پول از طریق پرداخت آنلاین",
                    transaction_type='charge'
                )
                return redirect(reverse_lazy("wallets:charge_success"))

        # پرداخت ناموفق
        payment_obj.status = PayemntStatusType.failed.value
        payment_obj.response_json = response
        payment_obj.save()

        order = getattr(payment_obj, "order", None)
        if order:
            send_bulk_sms(
                message_text=f"مشتری گرامی،\nسفارش شما {order.order_number} لغو شد.\nبرای اطلاعات بیشتر با پشتیبانی تماس بگیرید.\nمـــن مـــارکـــت",
                mobiles=[f"{order.user.phone_number}"]
            )
            order.status = OrderStatusType.failed.value
            order.save()
            return redirect(reverse_lazy("order:failed"))

        wallet = getattr(payment_obj, "wallet", None)
        if wallet:
            return redirect(reverse_lazy("wallets:charge_failed"))

        return redirect("/")
