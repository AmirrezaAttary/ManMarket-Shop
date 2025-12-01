from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from ..models import OTP
from ..forms import OTPVerifyForm


class OTPVerificationView(FormView):
    template_name = 'accounts/verify_otp.html'
    form_class = OTPVerifyForm
    success_url = reverse_lazy('dashboard:home')

    def get_initial(self):
        phone = self.request.session.get('otp_phone')
        return {"phone_number": phone} if phone else {}

    def form_valid(self, form):
        user = form.cleaned_data['user']
        user.is_active = True
        user.is_verified = True
        user.save()
        # --- مهم ---
        # تعیین backend تا Django بداند از کدام بک‌اند وارد می‌شود
        user.backend = 'django.contrib.auth.backends.ModelBackend'

        # لاگین
        login(self.request, user)

        # استفاده‌شدن OTP
        OTP.objects.filter(
            user=user, code=form.cleaned_data['code']
        ).update(is_used=True)

        messages.success(self.request, "ورود با موفقیت انجام شد.")
        return super().form_valid(form)
