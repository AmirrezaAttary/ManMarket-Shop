from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView as DjangoLoginView
from accounts.forms import CustomAuthenticationForm,RegisterForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from accounts.utils import send_password_reset_email,send_email_otp, send_sms_otp
from django.shortcuts import redirect
from django.contrib import messages  
from django.contrib.messages.views import SuccessMessageMixin
from accounts.models import OTP_LOGIN


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        # اگر کاربر تایید نشده بود → OTP بفرست و ریدایرکت کن
        if not user.is_verified and not user.is_phone_verified:
            otp = OTP_LOGIN.create_otp(user)

            if user.phone_number:
                send_sms_otp(user)
            elif user.email:
                send_email_otp(user)

            self.request.session['otp_user_id'] = user.id
            messages.info(self.request, "کد تأیید برای شما ارسال شد، لطفاً وارد کنید.")
            return redirect(reverse_lazy("accounts:verify_otp"))

        # اگر تایید شده بود → لاگین معمولی
        return super().form_valid(form)

    

class RegisterView(TemplateView):
    template_name = 'accounts/register.html'

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            otp = OTP_LOGIN.create_otp(user)

            if form.cleaned_data.get('is_email'):
                send_email_otp(user)
            else:
                send_sms_otp(user)


            messages.info(request, "کد تأیید برای شما ارسال شد. لطفاً آن را وارد کنید.")
            return redirect(reverse_lazy('accounts:verify_otp') + f"?user_id={user.id}")

        request.session['otp_user_id'] = user.id
        return redirect(reverse_lazy('accounts:verify_otp'))


class LogoutView(auth_views.LogoutView):
    pass


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'email/password_reset_email.tpl'
    subject_template_name = 'email/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    
    def form_valid(self, form):
        # دریافت ایمیل وارد شده
        email = form.cleaned_data.get('email')
        
        # جستجو برای کاربری با ایمیل وارد شده
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            reset_link = self.request.build_absolute_uri(f"/accounts/reset/{uid}/{token}/")
            
            # ارسال ایمیل به صورت غیر همزمان
            send_password_reset_email(self.request, email, reset_link)
        
        # ارسال پاسخ موفقیت‌آمیز
        return HttpResponseRedirect("/accounts/password_reset/done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
    