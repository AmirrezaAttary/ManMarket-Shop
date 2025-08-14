from accounts.forms import OTPRequestForm,OTPVerifyForm
from accounts.utils import send_otp
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages  
from accounts.models import User,OTP
from django.views.generic import FormView
from django.http import JsonResponse
from django.views import View


class OTPLoginRequestView(FormView):
    template_name = 'accounts/otp_request.html'
    form_class = OTPRequestForm

    def form_valid(self, form):
        phone = form.cleaned_data['phone_number']
        user = User.objects.get(phone_number=phone)
        send_otp(user)
        return redirect('accounts:otp_verify')  # یا پاس دادن phone_number با session


class OTPVerifyView(FormView):
    template_name = 'accounts/otp_verify.html'
    form_class = OTPVerifyForm

    def get_initial(self):
        phone = self.request.session.get('otp_phone')
        if not phone:
            return {}
        return {'phone_number': phone}

    def form_valid(self, form):
        phone = self.request.session.get('otp_phone')
        if not phone:
            messages.error(self.request, "اطلاعات شما منقضی شده است. دوباره تلاش کنید.")
            return redirect('accounts:otp_or_email_request')

        user = form.cleaned_data['user']
        user.backend = 'accounts.backends.EmailOrPhoneBackend'
        login(self.request, user)
        OTP.objects.filter(user=user, code=form.cleaned_data['code']).update(is_used=True)

        # پاک کردن از سشن
        del self.request.session['otp_phone']

        messages.success(self.request, "ورود شما با موفقیت انجام شد.")
        return redirect('dashboard:home')


class ResendPhoneOTPView(View):
    def post(self, request, *args, **kwargs):
        phone = request.session.get('otp_phone')
        if not phone:
            return JsonResponse({'status': 'error', 'message': 'شماره تلفن یافت نشد.'}, status=400)

        try:
            user = User.objects.get(phone_number=phone)
            send_otp(user)  # این همون تابعی باشه که کد SMS می‌فرسته
            return JsonResponse({'status': 'ok', 'message': 'کد جدید ارسال شد.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'کاربر یافت نشد.'}, status=404)