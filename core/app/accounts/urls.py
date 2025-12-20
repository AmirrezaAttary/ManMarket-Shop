from django.urls import path,include
from .api.v1 import urls as api_urls
from . import views

app_name = 'accounts'

urlpatterns = [
    # api accounts
    path('v1/', include(api_urls)),

    # User authentication
    path('login/', views.LoginView.as_view(), name="login"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('logout/', views.LogoutView.as_view(), name="logout"),

    # Password reset based on phone + OTP
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/verify/<str:phone>/', views.PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password_reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # OTP views
    path('otp/request/', views.OTPLoginRequestView.as_view(), name='otp_request'),
    path('otp/verify/', views.OTPVerificationView.as_view(), name='otp_verify'),
    path('phone-otp-resend/', views.ResendPhoneOTPView.as_view(), name='phone_otp_resend'),
]
