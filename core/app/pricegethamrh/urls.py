from django.urls import path,re_path
from . import views

app_name = "pricegethamrh"

urlpatterns = [
    path("getcolor/<int:pk>/",views.GetColorAndPrice.as_view(),name="getcolor"),
    path("update-all-hamrah/", views.UpdateAllHamrahProductsView.as_view(), name="update-all-hamrah"),
]