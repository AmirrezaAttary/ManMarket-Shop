from django.urls import path,re_path,include
from django.contrib.auth import views as auth_views
from .views import AdminLoginView
from .api.v1 import urls as api_v1_urls

app_name = "accounts"

urlpatterns = [
    path('v1/', include(api_v1_urls)),
    path("login/", AdminLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
