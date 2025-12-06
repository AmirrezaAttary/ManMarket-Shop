from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from ..models import User
from ..validators import validate_iranian_cellphone_number
from django.core.exceptions import ValidationError


class CustomAuthenticationForm(BaseAuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("کاربری با این مشخصات یافت نشد یا رمز اشتباه است.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data



class RegisterForm(forms.Form):
    phone_number = forms.CharField(label="شماره موبایل")
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput)

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number'].strip()
        current_user = self.initial.get('user')

        # اعتبارسنجی شماره موبایل
        validate_iranian_cellphone_number(phone)

        # چک کردن تکراری نبودن
        user_qs = User.objects.all()
        if current_user:
            user_qs = user_qs.exclude(pk=current_user.pk)

        if user_qs.filter(phone_number=phone).exists():
            raise ValidationError("این شماره موبایل قبلاً ثبت شده است.")

        return phone

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise ValidationError("رمزها یکسان نیستند")
        return p2

    def save(self, commit=True):
        phone_number = self.cleaned_data['phone_number']
        password = self.cleaned_data['password1']

        # چون ایمیل دیگر نداریم، برابر None قرار می‌دهیم
        user = User.objects.create_user(
            email=None,
            phone_number=phone_number,
            password=password
        )
        return user
