from django.urls import path,include
from . import views
from .api.v1 import urls as api_urls

app_name = "payment"

urlpatterns = [
    # api payment
    path("v1",include(api_urls)),

    path("verify",views.PaymentVerifyView.as_view(),name="verify"),
    path('refah/callback/', views.RefahCallbackView.as_view(), name='refah_callback'),  # مخصوص رفاه
]