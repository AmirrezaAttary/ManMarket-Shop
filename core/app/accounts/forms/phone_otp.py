from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import User,OTP
from ..validators import validate_iranian_cellphone_number
from django.core.exceptions import ValidationError


class OTPRequestForm(forms.Form):
    phone_number = forms.CharField(label='شماره موبایل')

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        validate_iranian_cellphone_number(phone)
        if not User.objects.filter(phone_number=phone).exists():
            raise ValidationError("کاربری با این شماره وجود ندارد.")
        return phone


class OTPVerifyForm(forms.Form):
    phone_number = forms.CharField(label='شماره موبایل')
    code = forms.CharField(label='کد تایید')

    def clean(self):
        phone = self.cleaned_data.get('phone_number')
        code = self.cleaned_data.get('code')
        user = User.objects.filter(phone_number=phone).first()
        if user:
            otp = OTP.objects.filter(user=user, code=code, is_used=False).last()
            if otp and otp.is_valid():
                self.cleaned_data['user'] = user
                return self.cleaned_data
        raise ValidationError("کد وارد شده نامعتبر است یا منقضی شده.")
    
    
class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, label="کد تأیید")