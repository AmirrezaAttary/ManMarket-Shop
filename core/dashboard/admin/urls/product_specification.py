from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("specification/list/",views.AdminGetSpecificationListView.as_view(),name="specification-list"),
    path("specification/add/",views.AdminGetSpecificationCreateView.as_view(),name="specification-add"),
    path("specification/<int:pk>/delete/",views.AdminGetSpecificationDeleteView.as_view(),name="specification-delete"),
    path("specification/<int:pk>/edit/",views.AdminGetSpecificationEditView.as_view(),name="specification-edit"),
    
    # edit one product specification
    path("specification/<int:pk>/delete-one/<int:prduct_pk>",views.AdminSpecificationDeleteView.as_view(),name="specification-one-delete"),
    path("specification/<int:pk>/add-one/",views.AdminSpecificationAddView.as_view(),name="specification-add-one"),
    path("specification/<int:pk>/edit-one/<int:prduct_pk>",views.AdminSpecificationEditView.as_view(),name="specification-edit-one"),
]