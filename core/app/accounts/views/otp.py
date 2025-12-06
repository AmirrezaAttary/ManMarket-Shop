from django.views.generic import FormView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login
from ..models import OTP,User
from ..forms import OTPVerifyForm, OTPRequestForm
from ..scripts import send_bulk_sms


class OTPLoginRequestView(FormView):
    template_name = 'accounts/otp_request.html'
    form_class = OTPRequestForm

    def form_valid(self, form):
        phone = form.cleaned_data['phone_number']
        user = User.objects.get(phone_number=phone)
        otp = OTP.create_otp(user)
        send_bulk_sms(f"کد ورود شما: {otp.code}",[phone])
        self.request.session['otp_phone'] = user.phone_number
        return redirect('accounts:otp_verify')  # یا پاس دادن phone_number با session


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


class ResendPhoneOTPView(View):
    def post(self, request, *args, **kwargs):
        phone = request.session.get('otp_phone')
        if not phone:
            return JsonResponse({'status': 'error', 'message': 'شماره همراه یافت نشد.'}, status=400)

        try:
            user = User.objects.get(phone_number=phone)
            # send_otp(user)  # این همون تابعی باشه که کد SMS می‌فرسته
            otp = OTP.create_otp(user)
            send_bulk_sms(f"کد جدید شما: {otp.code}", [phone])
            return JsonResponse({'status': 'ok', 'message': 'کد جدید ارسال شد.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'کاربر یافت نشد.'}, status=404)