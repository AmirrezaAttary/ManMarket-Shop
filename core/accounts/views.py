from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm,RegisterForm,ResendActivationEmailForm
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
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from accounts.models import User
from django.core.mail import send_mail
from django.views.generic import FormView
from django.utils.encoding import force_str



class LoginView(SuccessMessageMixin,auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    success_message = 'شما با موفقیت وارد من مارکت شدید'
    

class RegisterView(TemplateView):
    template_name = 'accounts/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return self.render_to_response({'form': RegisterForm()})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'accounts.backends.EmailOrPhoneBackend'
            login(request, user)
            messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد.')
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
    
    
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            messages.success(request, 'حساب شما با موفقیت فعال شد.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'لینک فعال‌سازی نامعتبر یا منقضی شده است.')
            return redirect('accounts:login')

   
class ResendActivationEmailView(FormView):
    template_name = "accounts/resend_activation.html"
    form_class = ResendActivationEmailForm
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_link = self.request.build_absolute_uri(
                    reverse_lazy('accounts:activate_account', kwargs={'uidb64': uid, 'token': token})
                )

                # ارسال ایمیل
                send_mail(
                    subject="فعال‌سازی حساب کاربری",
                    message=f"برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:\n{activation_link}",
                    from_email="info@manmarket.ir",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(self.request, "لینک فعال‌سازی به ایمیل شما ارسال شد.")
            else:
                messages.info(self.request, "حساب شما قبلاً فعال شده است.")
        except User.DoesNotExist:
            messages.error(self.request, "کاربری با این ایمیل یافت نشد.")

        return super().form_valid(form)