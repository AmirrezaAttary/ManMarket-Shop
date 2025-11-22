from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import User,EmailOTP,OTP
from ..validators import validate_iranian_cellphone_number
import re
from django.core.exceptions import ValidationError

class OTPOrEmailRequestForm(forms.Form):
    identifier = forms.CharField(label='ایمیل یا شماره موبایل')

    def clean_identifier(self):
        value = self.cleaned_data['identifier'].strip()

        # تشخیص ایمیل
        if re.match(r"[^@]+@[^@]+\.[^@]+", value):
            if not User.objects.filter(email=value).exists():
                raise ValidationError("کاربری با این ایمیل یافت نشد.")
            self.cleaned_data['type'] = 'email'
            return value

        # تشخیص شماره موبایل
        try:
            validate_iranian_cellphone_number(value)
        except ValidationError:
            raise ValidationError("لطفاً ایمیل معتبر یا شماره موبایل صحیح وارد کنید.")

        if not User.objects.filter(phone_number=value).exists():
            raise ValidationError("کاربری با این شماره موبایل یافت نشد.")

        self.cleaned_data['type'] = 'phone'
        return value
    
    
class EmailOTPVerifyForm(forms.Form):
    email = forms.EmailField(label='ایمیل')
    code = forms.CharField(label='کد ارسالی به ایمیل')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        code = cleaned_data.get('code')
        user = User.objects.filter(email=email).first()

        if user:
            otp = EmailOTP.objects.filter(user=user, code=code, is_used=False).last()
            if otp and otp.is_valid():
                cleaned_data['user'] = user
                return cleaned_data

        raise forms.ValidationError("کد وارد شده معتبر نیست یا منقضی شده.")
