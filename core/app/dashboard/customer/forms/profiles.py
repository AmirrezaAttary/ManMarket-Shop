from django.contrib.auth import forms as auth_forms
from django import forms
from django.utils.translation import gettext_lazy as _
from ....accounts.models import User,Profile
from django.core.exceptions import ValidationError


class CustomerPasswordChangeForm(auth_forms.PasswordChangeForm):
    error_messages = {
        "password_incorrect": _(
            "پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید."
        ),
        "password_mismatch": _("دو پسورد ورودی با همدیگر مطابقت ندارند"),
    }
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control text-center'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control text-center'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control text-center'
        self.fields['old_password'].widget.attrs['placeholder'] = "پسورد قبلی خود را وارد نمایید"
        self.fields['new_password1'].widget.attrs['placeholder'] = "پسورد جایگزین خود را وارد نمایید"
        self.fields['new_password2'].widget.attrs['placeholder'] = "پسورد جایگزین خود را مجدد وارد نمایید"
    

class CustomerProfileEditForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'profile__input',
            'placeholder': 'شماره همراه را وارد نمایید',
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'profile__input',
            'placeholder': 'ایمیل را وارد نمایید',
        })
    )
    code_melli = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'profile__input',
            'placeholder': 'کد ملی را وارد نمایید',
        })
    )

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "birth_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ست کردن placeholder و کلاس برای فیلدهای profile
        for field_name, placeholder in [
            ('first_name', 'نام خود را وارد نمایید'),
            ('last_name', 'نام خانوادگی را وارد نمایید'),
            ('birth_date', 'تاریخ تولد را وارد نمایید')
        ]:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs['class'] = 'profile__input'
                field.widget.attrs['placeholder'] = placeholder

        # مقداردهی اولیه فیلدهای user
        user = getattr(self.instance, 'user', None)
        if user:
            self.fields['phone_number'].initial = user.phone_number
            self.fields['email'].initial = user.email
            self.fields['code_melli'].initial = user.code_melli

            if user.is_verified:
                self.fields['phone_number'].disabled = True

    # ------------ Clean Methods -------------
    def clean_email(self):
        email = self.cleaned_data.get("email") or None
        qs = User.objects.filter(email=email)
        if self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError("ایمیل وارد شده قبلاً ثبت شده است.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number") or None
        qs = User.objects.filter(phone_number=phone)
        if self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError("شماره همراه وارد شده قبلاً ثبت شده است.")
        return phone

    def clean_code_melli(self):
        code = self.cleaned_data.get("code_melli") or None
        if code:
            if not code.isdigit() or len(code) != 10:
                raise ValidationError("کد ملی باید دقیقاً ۱۰ رقم عددی باشد.")
            if not self._validate_iranian_melli(code):
                raise ValidationError("کد ملی وارد شده معتبر نیست.")
            qs = User.objects.filter(code_melli=code)
            if self.instance.user:
                qs = qs.exclude(pk=self.instance.user.pk)
            if qs.exists():
                raise ValidationError("کد ملی وارد شده قبلاً ثبت شده است.")
        return code

    def _validate_iranian_melli(self, code):
        """اعتبارسنجی الگوریتمی کد ملی ایران"""
        if code in [str(i)*10 for i in range(10)]:
            return False
        check = int(code[9])
        s = sum(int(code[x]) * (10 - x) for x in range(9)) % 11
        return (s < 2 and check == s) or (s >= 2 and check == 11 - s)

    # ------------ Save Method -------------
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()

        user = getattr(profile, 'user', None)
        if user:
            user.phone_number = self.cleaned_data.get('phone_number') or None
            user.email = self.cleaned_data.get('email') or None
            user.code_melli = self.cleaned_data.get('code_melli') or None
            if commit:
                user.save()

        return profile

        