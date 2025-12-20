from django.urls import path, include
from .views import DashboardHomeAPIView

app_name = 'api-v1-dashboard'

urlpatterns = [
    path('', DashboardHomeAPIView.as_view(), name='home'),
    path('admin/', include('app.dashboard.api.v1.admin.urls')),
    path('user/', include('app.dashboard.api.v1.user.urls')),
]
