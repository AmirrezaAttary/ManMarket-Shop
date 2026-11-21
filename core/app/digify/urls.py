from django.urls import path, re_path

from .views import ProductDetailFeedView, ProductListFeedView

app_name = "digify"

urlpatterns = [
    re_path(r"^v1/products/?$", ProductListFeedView.as_view(), name="product-list"),
    re_path(r"^v1/products/(?P<pk>\d+)/?$", ProductDetailFeedView.as_view(), name="product-detail"),
]