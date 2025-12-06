from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from ..models import OTP
from ..forms import RegisterForm
from ..scripts import send_bulk_sms

class RegisterView(TemplateView):
    template_name = 'accounts/register.html'

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            otp = OTP.create_otp(user)

            send_bulk_sms(
                f"کد تأیید شما: {otp.code}",
                [user.phone_number]
            )

            # ✅ اینجا user وجود داره، پس درست ذخیره میشه
            self.request.session['otp_phone'] = user.phone_number

            messages.info(request, "کد تأیید برای شما ارسال شد. لطفاً آن را وارد کنید.")
            return redirect(reverse_lazy('accounts:otp_verify'))

        # اگر فرم معتبر نبود، نباید از user استفاده کنیم
        messages.error(request, "این کاربر قبلاً ثبت‌نام کرده است.")
        return redirect('accounts:register')