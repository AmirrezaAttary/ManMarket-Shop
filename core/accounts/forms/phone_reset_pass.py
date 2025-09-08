from django import forms

class PasswordResetForm(forms.Form):
    phone_number = forms.CharField(label="شماره موبایل", max_length=12)
    
    
class PasswordResetVerifyForm(forms.Form):
    code = forms.CharField(label="کد تایید", max_length=6)

class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(label="رمز عبور جدید", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="تکرار رمز عبور", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("new_password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("رمز عبور و تکرار آن یکسان نیست.")
        return cleaned_data