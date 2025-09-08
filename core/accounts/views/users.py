from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView as DjangoLoginView
from accounts.forms import *
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from accounts.utils import send_email_otp, send_sms_otp
from django.shortcuts import redirect
from django.contrib import messages  
from django.contrib.messages.views import SuccessMessageMixin
from accounts.models import OTP_LOGIN
from django.views.generic.edit import FormView
from accounts.utils import send_bulk_sms


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

            # ✅ اینجا user وجود داره، پس درست ذخیره میشه
            request.session['otp_user_id'] = user.id

            messages.info(request, "کد تأیید برای شما ارسال شد. لطفاً آن را وارد کنید.")
            return redirect(reverse_lazy('accounts:verify_otp') + f"?user_id={user.id}")

        # اگر فرم معتبر نبود، نباید از user استفاده کنیم
        messages.error(request, "این کاربر قبلاً ثبت‌نام کرده است.")
        return redirect('accounts:register')



class LogoutView(auth_views.LogoutView):
    pass


class PasswordResetView(FormView):
    template_name = "accounts/password_reset.html"
    form_class = PasswordResetForm

    def form_valid(self, form):
        phone = form.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone).first()

        if not user:
            messages.error(self.request, "کاربری با این شماره موبایل پیدا نشد.")
            return self.form_invalid(form)

        otp = OTP_LOGIN.create_otp(user)

        send_bulk_sms(
            message_text=f"کد بازیابی رمز عبور: {otp.code}\nمحرمانه نگه دارید!\nمـــن مـــارکـــت  - ارزش شما برای ما بـیـنـهـایـت است.",
            mobiles=[user.phone_number]
        )

        messages.success(self.request, "کد تایید برای شما ارسال شد.")
        return redirect("accounts:password_reset_verify", phone=phone)


class PasswordResetVerifyView(FormView):
    template_name = "accounts/password_reset_verify.html"
    form_class = PasswordResetVerifyForm

    def dispatch(self, request, *args, **kwargs):
        self.phone = kwargs.get("phone")
        self.user = User.objects.filter(phone_number=self.phone).first()
        if not self.user:
            messages.error(request, "کاربری پیدا نشد.")
            return redirect("accounts:password_reset")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        code = form.cleaned_data['code']
        otp = OTP_LOGIN.objects.filter(user=self.user, code=code, is_used=False).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            messages.error(self.request, "کد وارد شده معتبر نیست یا منقضی شده است.")
            return self.form_invalid(form)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        self.request.session["reset_user_id"] = self.user.id
        return redirect("accounts:password_reset_confirm")
    
    

class PasswordResetConfirmView(FormView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = PasswordResetConfirmForm
    success_url = "/accounts/login/"

    def form_valid(self, form):
        user_id = self.request.session.get("reset_user_id")
        if not user_id:
            messages.error(self.request, "جلسه شما منقضی شده است. دوباره تلاش کنید.")
            return redirect("accounts:password_reset")

        user = User.objects.get(id=user_id)
        user.set_password(form.cleaned_data['new_password'])
        user.save()

        # پاک کردن session
        self.request.session.pop("reset_user_id", None)

        messages.success(self.request, "رمز عبور شما با موفقیت تغییر یافت.")
        return super().form_valid(form)


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

# class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
#     template_name = 'accounts/password_reset_confirm.html'
#     success_url = reverse_lazy('accounts:password_reset_complete')

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
    