from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from ..accounts.models import UserType


class AdminOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse_lazy('accounts:login')}?next={request.path}")
        if request.user.type not in (UserType.admin.value, UserType.superuser.value):
            raise PermissionDenied("فقط ادمین و سوپر یوزر به پنل مدیریت دسترسی دارند.")
        return super().dispatch(request, *args, **kwargs)


class ProjectEntryView(View):
    """Single entry point for the project: login first, then the admin dashboard."""
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy("accounts:login"))
        if request.user.type in (UserType.admin.value, UserType.superuser.value):
            return redirect(reverse_lazy("dashboard:admin:home"))
        raise PermissionDenied("این پروژه فقط برای ادمین و سوپر یوزر در دسترس است.")


class DashboardHomeView(ProjectEntryView):
    pass
