from django.urls import path

from .views import (
    BWDKCompleteAPIView,
    BWDKCreateOrderAPIView,
    BWDKGetOrderAPIView,
    BWDKRefundOrderAPIView,
    BWDKVerifyOrderAPIView,
    BWDKWebhookAPIView,
)

app_name = "api-v1-bwdk"

urlpatterns = [
    path("create/", BWDKCreateOrderAPIView.as_view(), name="create"),
    path("complete/", BWDKCompleteAPIView.as_view(), name="complete"),
    path("orders/<uuid:order_uuid>/", BWDKGetOrderAPIView.as_view(), name="get"),
    path("orders/<uuid:order_uuid>/verify/", BWDKVerifyOrderAPIView.as_view(), name="verify"),
    path("webhook/", BWDKWebhookAPIView.as_view(), name="webhook"),
    path("orders/<uuid:order_uuid>/refund/", BWDKRefundOrderAPIView.as_view(), name="refund"),
]
