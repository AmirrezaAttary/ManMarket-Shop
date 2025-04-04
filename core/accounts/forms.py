from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError
from django import forms
from accounts.models import User

class AuthenticationForm(auth_forms.AuthenticationForm):
    def confirm_login_allowed(self, user):
        super(AuthenticationForm,self).confirm_login_allowed(user)
        

        
        

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