# payment/services.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .zarinpal_client import ZarinPalSandbox
from ..wallets.models import Wallet
from ..order.models import OrderStatusType
from .models import PaymentModel, PayemntStatusType, PayemntType

class PaymentService:

    def __init__(self, request):
        self.request = request
        self.user = request.user

    def pay(self, order, cart):
        payment_method = self.request.POST.get("payment_method")

        if payment_method == "wallet":
            return self._wallet(order)

        if payment_method == "zarinpal":
            return self._zarinpal(order)

        messages.error(self.request, "روش پرداخت نامعتبر است")
        return redirect("order:checkout")

    # ---------- WALLET ----------
    def _wallet(self, order):
        wallet = Wallet.objects.get(user=self.user)
        order.total_price += 50000

        if wallet.balance < order.total_price:
            messages.error(self.request, "موجودی کیف پول کافی نیست")
            return redirect("order:checkout")

        wallet.balance -= order.total_price
        wallet.save()

        payment = PaymentModel.objects.create(
            authority_id=f"WALLET-{timezone.now().timestamp()}",
            amount=order.total_price,
            status=PayemntStatusType.success,
            wallet=wallet,
            order=order,
            payemnt_type=PayemntType.wallet.value,
            response_json={"code": 100}
        )

        order.payment = payment
        order.status = OrderStatusType.awaiting.value
        order.save()

        return redirect("order:completed")

    # ---------- ZARINPAL ----------
    def _zarinpal(self, order):
        zarinpal = ZarinPalSandbox()
        order.total_price += 50000

        callback = self.request.build_absolute_uri(
            reverse("payment:verify")
        )

        response = zarinpal.payment_request(callback, order.total_price)

        if not isinstance(response, dict):
            messages.error(self.request, "پاسخ نامعتبر از درگاه")
            return redirect("order:checkout")

        authority = response.get("data", {}).get("authority")
        if not authority:
            messages.error(self.request, "خطا در ارتباط با زرین‌پال")
            return redirect("order:checkout")

        payment = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.total_price,
            order=order,
            payemnt_type=PayemntType.cart.value
        )

        order.payment = payment
        order.save()

        return redirect(zarinpal.generate_payment_url(authority))
