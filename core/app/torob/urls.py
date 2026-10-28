from django.urls import re_path

from .views import TorobProductsView

app_name = "torob"

urlpatterns = [
    # Torob's examples use no trailing slash; accept both so a POST is never redirected.
    re_path(r"^v3/products/?$", TorobProductsView.as_view(), name="products"),
]
