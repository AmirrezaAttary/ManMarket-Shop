from django.urls import path
from . import views

app_name = 'api-v1-payment'

urlpatterns = [
    # آدرس callback که سامان بعد از پرداخت کاربر را با POST به آن برمی‌گرداند
    path("verify/", views.PaymentVerifyAPIView.as_view(), name="verify"),
    # صفحه‌ی واسط: فرم POST خودکار به درگاه سامان
    path("redirect/<str:token>/", views.saman_redirect, name="redirect"),
]