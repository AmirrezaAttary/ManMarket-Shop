from django.urls import path,include
from .api.v1 import urls

app_name = "cart"

urlpatterns = [
    path('v1/', include(urls)),

]

