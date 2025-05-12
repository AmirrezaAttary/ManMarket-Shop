from django.urls import path,re_path
from . import views

app_name = "getspecification"

urlpatterns = [
    path("specification/<int:pk>/",views.GetSpecification.as_view(),name="specification"),

]