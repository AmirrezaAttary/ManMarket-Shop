from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm,RegisterForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from accounts.utils import send_password_reset_email
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages  





class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    

class RegisterView(TemplateView):
    template_name = 'accounts/register.html'

    def get(self, request, *args, **kwargs):
        # بررسی اینکه آیا کاربر وارد شده است
        if request.user.is_authenticated:
            return redirect('dashboard:home')  # به صفحه داشبورد هدایت کن
        return self.render_to_response({'form': RegisterForm()})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')  # به صفحه داشبورد هدایت کن

        messages.add_message(request, messages.SUCCESS, 'You have successfully logged')
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)  # ورود خودکار پس از ثبت‌نام
            return redirect(self.get_success_url())
        return self.render_to_response({'form': form})

    def get_success_url(self):
        return reverse_lazy('website:index')

    
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