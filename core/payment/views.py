from django.shortcuts import render
from django.views.generic import View
from .models import PaymentModel, PayemntStatusType,PayemntType
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from .zarinpal_client import ZarinPalSandbox
from order.models import OrderModel, OrderStatusType
from wallets.models import WalletTransaction
from cart.cart import CartSession
from cart.models import CartModel
from shop.models import ProductColorInventory
from accounts.scripts import send_bulk_sms
from django.contrib import messages


# Create your views here.

# payment/views.py


class PaymentVerifyView(View):
    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority")
        status = request.GET.get("Status")
        payment_obj = get_object_or_404(PaymentModel, authority_id=authority_id)

        zarin_pal = ZarinPalSandbox()
        response = zarin_pal.payment_verify(int(payment_obj.amount), payment_obj.authority_id)

        if status == 'OK' and response.get("data"):
            # ✅ ثبت اطلاعات پرداخت
            payment_obj.ref_id = response["data"].get("ref_id")
            payment_obj.response_code = response["data"].get("code")
            payment_obj.status = PayemntStatusType.success.value
            payment_obj.response_json = response
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order is not None:
                # 🔻 تغییر وضعیت سفارش
                order.status = OrderStatusType.awaiting.value
                order.save()

                # 🔻 کم کردن موجودی محصولات از انبار
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
                            # 🚨 در صورت کمبود موجودی بعد از پرداخت
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

                # 🔻 اگر پرداخت ترکیبی بود (کیف پول + درگاه)
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

                # 🔻 پیامک به مشتری و مدیر
                send_bulk_sms(
                    message_text=f"مشتری گرامی،\nسفارش شما {order.order_number} تأیید شد\nدر حال آماده‌سازی است.\nمـــن مـــارکـــت",
                    mobiles=[f"{order.user.phone_number}"]
                )
                send_bulk_sms(
                    message_text="یک سفارش جدید در من مارکت ثبت شد !",
                    mobiles=["09120983411"]
                )

                # 🔻 پاکسازی سبد خرید
                cart = CartModel.objects.filter(user=order.user).first()
                if cart:
                    cart.cart_items.all().delete()
                    CartSession(request.session).clear()

                return redirect(reverse_lazy("order:completed"))

            # 🔻 اگر پرداخت برای کیف پول بود
            wallet = getattr(payment_obj, "wallet", None)
            if wallet is not None:
                wallet.balance += payment_obj.amount
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=payment_obj.amount,
                    description="شارژ کیف پول از طریق پرداخت آنلاین",
                    transaction_type='charge'
                )
                return redirect(reverse_lazy("wallets:charge_success"))

            return redirect("/")

        else:
            # ❌ پرداخت ناموفق
            payment_obj.status = PayemntStatusType.failed.value
            payment_obj.response_code = response.get("errors", {}).get("code")
            payment_obj.response_json = response
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order is not None:
                send_bulk_sms(
                    message_text=f"مشتری گرامی،\nسفارش شما {order.order_number} لغو شد.\nبرای اطلاعات بیشتر با پشتیبانی تماس بگیرید.\nمـــن مـــارکـــت",
                    mobiles=[f"{order.user.phone_number}"]
                )

                order.status = OrderStatusType.failed.value
                order.save()
                return redirect(reverse_lazy("order:failed"))

            wallet = getattr(payment_obj, "wallet", None)
            if wallet is not None:
                return redirect(reverse_lazy("wallets:charge_failed"))

            return redirect("/")
