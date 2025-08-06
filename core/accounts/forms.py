from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from accounts.models import User, Profile
from accounts.validators import validate_iranian_cellphone_number
from django.core.exceptions import ValidationError



class AuthenticationForm(BaseAuthenticationForm):
    username = forms.CharField(
        label=_("ایمیل یا شماره تلفن"),
        widget=forms.TextInput(attrs={"autofocus": True}),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("کاربری با این مشخصات یافت نشد یا رمز اشتباه است.")
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

        

class RegisterForm(forms.Form):
    email_or_phone = forms.CharField(label="ایمیل یا شماره موبایل")
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput)

    def clean_email_or_phone(self):
        value = self.cleaned_data['email_or_phone'].strip()
        if '@' in value:
            # ایمیل
            if User.objects.filter(email__iexact=value).exists():
                raise ValidationError("این ایمیل قبلاً استفاده شده است.")
            self.cleaned_data['is_email'] = True
        else:
            # شماره موبایل
            validate_iranian_cellphone_number(value)
            if User.objects.filter(phone_number=value).exists():
                raise ValidationError("این شماره موبایل قبلاً استفاده شده است.")
            self.cleaned_data['is_email'] = False
        return value

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise ValidationError("رمزها یکسان نیستند")
        return p2

    def save(self, commit=True):
        email_or_phone = self.cleaned_data['email_or_phone']
        password = self.cleaned_data['password1']
        is_email = self.cleaned_data.get('is_email', True)

        if is_email:
            user = User.objects.create_user(email=email_or_phone, password=password)
        else:
            # مشخصاً مقدار email را برابر با None قرار می‌دهیم
            user = User.objects.create_user(email=None, phone_number=email_or_phone, password=password)

        return user
