from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("category/list/",views.AdminProductCategoryListView.as_view(),name="category-list"),
    path("category/add/",views.AdminProductCategoryCreateView.as_view(),name="category-add"),
    path("category/<int:pk>/delete/",views.AdminProductCategoryDeleteView.as_view(),name="category-delete"),
    path("category/<int:pk>/edi/",views.AdminProductCategoryEditView.as_view(),name="category-edit"),
]