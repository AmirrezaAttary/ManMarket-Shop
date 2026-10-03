from django.urls import path,re_path,include
from . import views

app_name = 'api-v1-order'

urlpatterns = [
    path("checkout/",views.OrderCheckOutAPIView.as_view(),name="checkout"),
]