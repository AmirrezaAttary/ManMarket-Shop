from accounts.forms import OTPRequestForm,OTPVerifyForm
from accounts.utils import send_otp
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages  
from accounts.models import User,OTP
from django.views.generic import FormView


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

    def form_valid(self, form):
        user = form.cleaned_data['user']
        login(self.request, user)
        OTP.objects.filter(user=user, code=form.cleaned_data['code']).update(is_used=True)
        messages.success(self.request, "ورود با موفقیت انجام شد.")
        return redirect('dashboard:home')
