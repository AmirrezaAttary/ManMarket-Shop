from django.views.generic import (
    View,
    UpdateView,
    ListView,
    DeleteView,
    CreateView,
    DetailView
)
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from django.core.exceptions import FieldError

from accounts.models import User,UserType


class AdminUsersListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/users/users-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = User.objects.all()
        
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(email__icontains=search_q) |
                Q(id__iexact=search_q) |
                Q(user_profile__phone_number__icontains=search_q) |
                Q(user_profile__first_name__icontains=search_q) |
                Q(user_profile__last_name__icontains=search_q)
            )

        # 🆕 فیلتر وضعیت انتشار
        if type := self.request.GET.get("type"):
            try:
                type = int(type)
                if type in dict(UserType.choices):
                    queryset = queryset.filter(type=type)
            except ValueError:
                pass

        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()

        # 🆕 اضافه کردن گزینه‌های فیلتر وضعیت به context
        context["type_choices"] = UserType.choices
        context["current_type_filter"] = self.request.GET.get("type")
        return context
    
    
    
class AdminUsersDetailView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/users/users-detail.html"
    model = User  # اضافه کردن model برای اینکه DetailView به درستی کار کند

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context["order_count"] = user.order_user.count()
        context["wishlist_count"] = user.wishlist_user.count()
        context["reviw_count"] = user.reviw_user.count()
        context["customer_chat_count"] = user.customer_chats.count()
        return context