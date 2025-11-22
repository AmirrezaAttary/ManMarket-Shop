# wallets/urls.py
from django.urls import path
from .views import WalletChargeView,WalletChargeSuccessView,WalletChargeFailedView

app_name = "wallets"

urlpatterns = [
    path("charge/", WalletChargeView.as_view(), name="charge"),
    path("charge/success/", WalletChargeSuccessView.as_view(), name="charge_success"),
    path("charge/failed/", WalletChargeFailedView.as_view(), name="charge_failed"),
]
