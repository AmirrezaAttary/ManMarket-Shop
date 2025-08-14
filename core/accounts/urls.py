from django.urls import path,include
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/',views.LoginView.as_view(),name="login"),
    path('register/',views.RegisterView.as_view(),name="register"),
    path('logout/',views.LogoutView.as_view(),name="logout"),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate_account'),
    path('resend-activation/', views.ResendActivationEmailView.as_view(), name='resend_activation'),
    path('login/email-otp/', views.OTPOrEmailRequestView.as_view(), name='otp_or_email_request'),
    path('login/email-otp/verify/', views.EmailOTPVerifyView.as_view(), name='email_otp_verify'),
    path('otp/request/', views.OTPLoginRequestView.as_view(), name='otp_request'),
    path('otp/verify/', views.OTPVerifyView.as_view(), name='otp_verify'),
    path('email-otp-resend/', views.ResendEmailOTPView.as_view(), name='email_otp_resend'),
    path('phone-otp-resend/', views.ResendPhoneOTPView.as_view(), name='phone_otp_resend'),


]