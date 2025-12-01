from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from ..forms import CustomAuthenticationForm
from ..models import OTP
from ..utils import send_email_otp, send_sms_otp

class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        # اگر کاربر تایید نشده بود → OTP بفرست و ریدایرکت کن
        if not user.is_verified:
            otp = OTP.create_otp(user)

            if user.phone_number:
                send_sms_otp(user)
            elif user.email:
                send_email_otp(user)

            self.request.session['otp_user_id'] = user.id
            messages.info(self.request, "کد تأیید برای شما ارسال شد، لطفاً وارد کنید.")
            return redirect(reverse_lazy("accounts:verify_otp"))

        # اگر تایید شده بود → لاگین معمولی
        return super().form_valid(form)

    