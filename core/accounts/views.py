from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from accounts.utils import send_password_reset_email


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    
    
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