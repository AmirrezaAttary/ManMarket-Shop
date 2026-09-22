from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .models import UserType


class AdminAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.type not in (UserType.admin.value, UserType.superuser.value):
            raise forms.ValidationError(
                "فقط مدیران و سوپر یوزرها اجازه ورود به پنل مدیریت را دارند.",
                code="not_admin",
            )


class AdminLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = AdminAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return str(reverse_lazy("dashboard:admin:profile-edit"))
