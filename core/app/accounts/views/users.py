from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.views.generic.edit import FormView
from ..forms import *
from ..models import User , OTP
from ..scripts import send_bulk_sms



class PasswordResetView(FormView):
    template_name = "accounts/password_reset.html"
    form_class = PasswordResetForm

    def form_valid(self, form):
        phone = form.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone).first()

        if not user:
            messages.error(self.request, "کاربری با این شماره موبایل پیدا نشد.")
            return self.form_invalid(form)

        otp = OTP.create_otp(user)

        send_bulk_sms(
            message_text=f"کد بازیابی رمز عبور: {otp.code}\nمحرمانه نگه دارید.\nمن مارکت -ارزش شما برای ما بینهایـت است.",
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
        otp = OTP.objects.filter(user=self.user, code=code, is_used=False).order_by('-created_at').first()

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


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
    