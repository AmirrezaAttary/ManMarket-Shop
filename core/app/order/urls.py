from django.urls import path,re_path,include
from . import views
from .api.v1 import urls as api_urls

app_name = "order"

urlpatterns = [
    # api order
    path('v1/', include(api_urls)),
    
    path("validate-coupon/",views.ValidateCouponView.as_view(),name="validate-coupon"),
    path("checkout/",views.OrderCheckOutView.as_view(),name="checkout"),
    path("completed/",views.OrderCompletedView.as_view(),name="completed"),
    path("failed/",views.OrderFailedView.as_view(),name="failed"),
    path("retry-payment/<int:order_id>/", views.OrderRetryPaymentView.as_view(), name="retry-payment"),

]