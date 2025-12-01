from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView as DjangoLoginView
from ..models import OTP
from ..forms import CustomAuthenticationForm
from ..scripts import send_bulk_sms

class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        # اگر کاربر تأیید نشده است → OTP ارسال کن
        if not user.is_verified:

            otp = OTP.create_otp(user)  # ← اصلاح شد

            if user.phone_number:
                send_bulk_sms(
                    f"کد تأیید شما: {otp.code}",
                    [user.phone_number]
                )
            else:   
                messages.error(self.request, "شماره موبایل برای ارسال کد تأیید موجود نیست.")
                return redirect(reverse_lazy("accounts:login"))

            self.request.session['otp_phone'] = user.phone_number
            messages.info(self.request, "کد تأیید برای شما ارسال شد.")
            return redirect(reverse_lazy("accounts:otp_verify"))

        # اگر تایید شده بود → ورود معمولی
        return super().form_valid(form)
