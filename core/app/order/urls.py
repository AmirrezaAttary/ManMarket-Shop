from django.urls import path,re_path,include
from . import views
from .api.v1 import urls as api_urls

app_name = "order"

urlpatterns = [
    # api order
    path('v1/', include(api_urls)),
    path("checkout/address/", views.CheckoutAddressView.as_view(), name="checkout-address"),
    path("checkout/shipping/", views.CheckoutShippingView.as_view(), name="checkout-shipping"),
    path("checkout/payment/", views.CheckoutPaymentView.as_view(), name="checkout-payment"),
    path("validate-coupon/",views.ValidateCouponView.as_view(),name="validate-coupon"),
    path("checkout/",views.OrderCheckOutView.as_view(),name="checkout"),
    path("completed/",views.OrderCompletedView.as_view(),name="completed"),
    path("failed/",views.OrderFailedView.as_view(),name="failed"),
    path("retry-payment/<int:order_id>/", views.OrderRetryPaymentView.as_view(), name="retry-payment"),

]