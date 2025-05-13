from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("specification/list/",views.AdminGetSpecificationListView.as_view(),name="specification-list"),
    path("specification/add/",views.AdminGetSpecificationCreateView.as_view(),name="specification-add"),
    path("specification/<int:pk>/delete/",views.AdminGetSpecificationDeleteView.as_view(),name="specification-delete"),
    path("specification/<int:pk>/edi/",views.AdminGetSpecificationEditView.as_view(),name="specification-edit"),
]