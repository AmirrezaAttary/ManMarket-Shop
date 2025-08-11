from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from accounts.models import User, Profile, EmailOTP,OTP
from accounts.validators import validate_iranian_cellphone_number
from django.core.exceptions import ValidationError

class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(label="ایمیل", widget=forms.EmailInput(attrs={'class': 'form-control'}))

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
        user_qs = User.objects.all()
        current_user = self.initial.get('user')  # کاربر جاری برای فرم ویرایش

        if '@' in value:
            # ایمیل
            if current_user:
                user_qs = user_qs.exclude(pk=current_user.pk)
            if user_qs.filter(email__iexact=value).exists():
                raise ValidationError("این ایمیل قبلاً ثبت شده است.")
            self.cleaned_data['is_email'] = True
        else:
            # شماره موبایل
            validate_iranian_cellphone_number(value)
            if current_user:
                user_qs = user_qs.exclude(pk=current_user.pk)
            if user_qs.filter(phone_number=value).exists():
                raise ValidationError("این شماره موبایل قبلاً ثبت شده است.")
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




# accounts/forms.py

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



# accounts/forms.py

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
