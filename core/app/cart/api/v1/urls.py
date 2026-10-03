from django.urls import path,re_path,include
from . import views


app_name = 'api-v1-cart'

urlpatterns = [
    path("cart/",views.CartRetrieveAPIView.as_view(),name="cart-detail"),
    path("cart/add-product/",views.CartAddProductCreateAPIView.as_view(),name="cart-add-product"),
    path("cart/update-product/<int:pk>/",views.CartUpdateAPIView.as_view(),name="cart-update-product"),
    path("cart/delete-product/<int:pk>/",views.CartItemDestroyAPIView.as_view(),name="cart-delete-product"),
]

# carts/urls.py

