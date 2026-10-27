from django.urls import path

from .views import ProductDetailFeedView, ProductListFeedView

app_name = "digify"

urlpatterns = [
    path("v1/products/", ProductListFeedView.as_view(), name="product-list"),
    path("v1/products/<int:pk>/", ProductDetailFeedView.as_view(), name="product-detail"),
]
