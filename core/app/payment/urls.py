from django.urls import path,include

from .api.v1 import urls as api_urls

app_name = "payment"

urlpatterns = [
    # api payment
    path("v1/",include(api_urls)),

]