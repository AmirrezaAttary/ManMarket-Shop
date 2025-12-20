from django.urls import path,re_path,include
from . import views
app_name = 'api-v1-payment'

urlpatterns = [
    path("verify/",views.PaymentVerifyAPIView.as_view(),name="verify"),
]