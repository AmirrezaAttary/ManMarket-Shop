from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("colors/list/",views.AdminGetColorListView.as_view(),name="colors-list"),
    path("colors/add/",views.AdminGetColorCreateView.as_view(),name="colors-add"),
    path("colors/<int:pk>/delete/",views.AdminGetColorDeleteView.as_view(),name="colors-delete"),
    path("colors/<int:pk>/edit/",views.AdminGetColorEditView.as_view(),name="colors-edit"),
    path("check-hamrah-status/", views.check_hamrah_status, name="check_hamrah_status"),
]