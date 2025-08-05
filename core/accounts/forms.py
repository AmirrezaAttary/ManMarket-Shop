from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from accounts.models import User, Profile


class AuthenticationForm(BaseAuthenticationForm):
    username = forms.CharField(
        label=_("ایمیل یا شماره تلفن"),
        widget=forms.TextInput(attrs={"autofocus": True}),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = self.get_user_by_email_or_phone(username)

            if user:
                self.user_cache = authenticate(
                    self.request, username=user.email, password=password
                )
                if self.user_cache is None:
                    raise forms.ValidationError("رمز عبور اشتباه است.")
                else:
                    self.confirm_login_allowed(self.user_cache)
            else:
                raise forms.ValidationError("کاربری با این مشخصات یافت نشد.")
        return self.cleaned_data

    def get_user_by_email_or_phone(self, identifier):
        """بررسی اینکه ورودی ایمیل است یا شماره و بازگرداندن یوزر مناسب"""
        try:
            if "@" in identifier:
                return User.objects.get(email__iexact=identifier)
            else:
                return User.objects.get(user_profile__phone_number=identifier)
        except User.DoesNotExist:
            return None

    def get_user(self):
        return self.user_cache


        
        

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']

    def clean_password2(self):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
            raise forms.ValidationError("رمزها یکسان نیستند")
        return self.cleaned_data.get('password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user