# wallets/views.py
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy,reverse
from wallets.permissions import HasCustomerAccessPermission
from wallets.forms import WalletChargeForm
from payment.models import PaymentModel
from payment.zarinpal_client import ZarinPalSandbox
from django.views.generic import TemplateView
from wallets.models import Wallet




class WalletChargeSuccessView(TemplateView):
    template_name = "wallets/charge_success.html"



class WalletChargeFailedView(TemplateView):
    template_name = "wallets/charge_failed.html"



class WalletChargeView(HasCustomerAccessPermission,View):
    def get(self, request):
        form = WalletChargeForm()
        return render(request, "wallets/wallet_charge.html", {"form": form})

    def post(self, request):
        form = WalletChargeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            zarinpal = ZarinPalSandbox()
            callback_url = request.build_absolute_uri(reverse_lazy("payment:verify"))
            result = zarinpal.payment_request(callback_url=callback_url, amount=amount)

            if result.get("data") and result["data"]["code"] == 100:
                authority = result["data"]["authority"]
                wallet = Wallet.objects.get(user=request.user)
                PaymentModel.objects.create(
                    authority_id=authority,
                    amount=amount,
                    wallet=wallet,
                )
                return redirect(zarinpal.generate_payment_url(authority))
            else:
                return render(request, "wallets/wallet_charge.html", {
                    "form": form,
                    "error": result.get("errors", {}).get("message", "خطا در ارتباط با درگاه پرداخت.")
                })
        return render(request, "wallets/wallet_charge.html", {"form": form})


class WalletChargeRequestView(View):
    def post(self, request):
        amount = int(request.POST.get("amount"))  # از فرم بگیر
        wallet = request.user.wallet

        payment_obj = PaymentModel.objects.create(
            amount=amount,
            wallet=wallet,
        )

        callback_url = request.build_absolute_uri(reverse("payment:verify"))
        zarinpal = ZarinPalSandbox()
        response = zarinpal.payment_request(callback_url, amount, "افزایش موجودی کیف پول")

        if response.get("data") and response["data"].get("authority"):
            authority_id = response["data"]["authority"]
            payment_obj.authority_id = authority_id
            payment_obj.save()
            return redirect(zarinpal.generate_payment_url(authority_id))
        else:
            # مدیریت خطا
            return redirect("wallets:charge_failed")