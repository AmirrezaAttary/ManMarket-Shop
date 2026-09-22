from django.urls import path,re_path,include

from .api.v1 import urls as api_urls

app_name = "order"

urlpatterns = [
    # api order
    path('v1/', include(api_urls)),

]