from django.urls import path,include

from .api.v1 import urls as api_urls

app_name = "review"

urlpatterns = [
    path("v1/",include(api_urls)),

]