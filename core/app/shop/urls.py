from django.urls import path,re_path,include
from .api.v1 import urls

app_name = 'shop'

urlpatterns = [
    path('v1/', include(urls)),

    
]