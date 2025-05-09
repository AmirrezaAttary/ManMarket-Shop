from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("product/<int:pk>/delete-color/<int:prduct_pk>",views.AdminProductColorDeleteView.as_view(),name="product-color-delete"),
    path("product/<int:pk>/add-color/",views.AdminProductAddColorView.as_view(),name="product-add-color"),
    path("product/<int:pk>/edit-color/<int:prduct_pk>",views.AdminProductEditColorView.as_view(),name="product-edit-color"),
]