from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("brand/list/",views.AdminProductBrandListView.as_view(),name="brand-list"),
    path("brand/add/",views.AdminProductBrandCreateView.as_view(),name="brand-add"),
    path("brand/<int:pk>/delete/",views.AdminProductBrandDeleteView.as_view(),name="brand-delete"),
    path("brand/<int:pk>/edi/",views.AdminProductBrandEditView.as_view(),name="brand-edit"),
]