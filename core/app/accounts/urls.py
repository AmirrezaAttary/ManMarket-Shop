from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # User authentication
    path('login/', views.LoginView.as_view(), name="login"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('logout/', views.LogoutView.as_view(), name="logout"),

    # Password reset based on phone + OTP
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/verify/<str:phone>/', views.PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password_reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('otp/request/', views.OTPLoginRequestView.as_view(), name='otp_request'),
    path('otp/verify/', views.OTPVerificationView.as_view(), name='otp_verify'),
    path('phone-otp-resend/', views.ResendPhoneOTPView.as_view(), name='phone_otp_resend'),
    path("send-phone-otp/", views.SendPhoneOTPView.as_view(), name="send_phone_otp"),
    path("verify-phone/", views.VerifyPhoneView.as_view(), name="verify_phone"),
]
