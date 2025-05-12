from django.urls import path,re_path
from . import views

app_name = "pricegethamrh"

urlpatterns = [
    path("getcolor/<int:pk>/",views.GetColorAndPrice.as_view(),name="getcolor"),

]