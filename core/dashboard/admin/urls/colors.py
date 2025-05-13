from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("color/list/",views.AdminColorListView.as_view(),name="color-list"),
    path("color/add/",views.AdminColorCreateView.as_view(),name="color-add"),
    path("color/<int:pk>/delete/",views.AdminColorDeleteView.as_view(),name="color-delete"),
    path("color/<int:pk>/edi/",views.AdminColorEditView.as_view(),name="color-edit"),
]