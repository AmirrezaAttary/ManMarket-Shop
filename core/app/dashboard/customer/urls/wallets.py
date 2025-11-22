from django.urls import path,include
from .. import views

urlpatterns = [
    path("wallet/Detail/",views.WalletDetailView.as_view(),name="wallet-detail"),
]