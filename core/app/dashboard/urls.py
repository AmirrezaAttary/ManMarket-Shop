from django.urls import path,include
from . import views
from . admin import urls as admin_urls
from . customer import urls as customer_urls

app_name = "dashboard"

urlpatterns = [
    path("home/",views.DashboardHomeView.as_view(),name="home"),
    
    # include admin urls
    path("admin/",include(admin_urls)),
    
    # # include customer urls
    path("customer/",include(customer_urls)),
]


