from django.urls import path,include

from . admin import urls as admin_urls
from .api.v1 import urls as api_urls
from . import views

app_name = "dashboard"

urlpatterns = [
    # api dashboard
    path('v1/', include(api_urls)),

    path("home/",views.DashboardHomeView.as_view(),name="home"),
    
    # include admin urls
    path("admin/",include(admin_urls)),
    
    # # include customer urls
    # path("customer/",include(customer_urls)),
]


