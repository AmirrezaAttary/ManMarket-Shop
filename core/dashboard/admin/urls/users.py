from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("users/list/",views.AdminUsersListView.as_view(),name="users-list"),
    # path("product/create/",views.AdminProductCreateView.as_view(),name="product-create"),
    # path("product/<int:pk>/edit/",views.AdminProductEditView.as_view(),name="product-edit"),
    # path("product/<int:pk>/delete/",views.AdminProductDeleteView.as_view(),name="product-delete"),
    # path("product/<int:pk>/add-image/",views.AdminProductAddImageView.as_view(),name="product-add-image"),
    # path("product/<int:pk>/image/<int:image_id>/remove/",views.AdminProductRemoveImageView.as_view(),name="product-remove-image"),
    # path("product/<int:pk>/add-color/",views.AdminProductAddColorView.as_view(),name="product-add-color"),
    # path("product/<int:pk>/edit-color/<int:prduct_pk>",views.AdminProductEditColorView.as_view(),name="product-edit-color"),
    # path('product/<int:pk>/image/<int:image_id>/update-color/',views.AdminProductChangeColorImageView.as_view(),name='product-update-image-color'),
]