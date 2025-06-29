from django.shortcuts import render
from django.views.generic import View
from .models import PaymentModel, PayemntStatusType
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from .zarinpal_client import ZarinPalSandbox
from order.models import OrderModel, OrderStatusType
from wallets.models import WalletTransaction
from cart.cart import CartSession
from cart.models import CartModel
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# Create your views here.

# payment/views.py

@method_decorator(cache_page(60 * 15), name='dispatch')
class PaymentVerifyView(View):
    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority")
        status = request.GET.get("Status")
        payment_obj = get_object_or_404(PaymentModel, authority_id=authority_id)

        zarin_pal = ZarinPalSandbox()
        response = zarin_pal.payment_verify(int(payment_obj.amount), payment_obj.authority_id)

        if status == 'OK' and response.get("data"):
            payment_obj.ref_id = response["data"].get("ref_id")
            payment_obj.response_code = response["data"].get("code")
            payment_obj.status = PayemntStatusType.success.value
            payment_obj.response_json = response
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order is not None:
                order.status = OrderStatusType.success.value
                order.save()

                cart = CartModel.objects.filter(user=order.user).first()
                if cart:
                    cart.cart_items.all().delete()
                    CartSession(request.session).clear()
                return redirect(reverse_lazy("order:completed"))

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
            payment_obj.status = PayemntStatusType.failed.value
            payment_obj.response_code = response.get("errors", {}).get("code")
            payment_obj.response_json = response
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order is not None:
                order.status = OrderStatusType.failed.value
                order.save()
                return redirect(reverse_lazy("order:failed"))

            wallet = getattr(payment_obj, "wallet", None)
            if wallet is not None:
                return redirect(reverse_lazy("wallets:charge_failed"))

            return redirect("/")


