from django import forms
from django.utils.translation import gettext_lazy as _
from accounts.models import User,EmailOTP

class EmailOTPRequestForm(forms.Form):
    email = forms.EmailField(label='ایمیل')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("کاربری با این ایمیل یافت نشد.")
        return email



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
