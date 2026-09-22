from django.urls import path
from django.contrib.auth import views as auth_views
from .views import AdminLoginView

app_name = "accounts"

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
