from django.urls import path,re_path,include
from .api.v1 import urls as api_v1_urls

app_name = 'blog'

urlpatterns = [
    path('v1/', include(api_v1_urls)),
]