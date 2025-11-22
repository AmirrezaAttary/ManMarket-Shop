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
from ...permissions import HasAdminAccessPermission
from django.core.exceptions import FieldError

from ....accounts.models import User,UserType
from ....wallets.models import Wallet
from ....shop.models import WishlistProductModel
from ....order.models import OrderModel,OrderStatusType
from ....review.models import ReviewModel,ReviewStatusType
from ....chat.models import ChatRoom


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
                Q(phone_number__icontains=search_q) |
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
    
    
class AdminUsersDetailWalletView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/users/users-wallet.html"
    model = Wallet
    
    def get_queryset(self):
        return Wallet.objects.all()
    
    
class AdminUsersDetailWishlistView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/users/users-wishlist.html"

    model = WishlistProductModel

    def get_queryset(self):
        user_pk = self.kwargs.get('pk')
        return WishlistProductModel.objects.filter(user_id=user_pk)
    
    
class AdminUsersDetailOrderView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/users/users-order.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        user_pk = self.kwargs.get("pk")
        queryset = OrderModel.objects.filter(user_id=user_pk)

        # فیلتر جستجو
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(id__icontains=search_q)

        # فیلتر وضعیت
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # مرتب‌سازی
        order_by = self.request.GET.get("order_by")
        if order_by:
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["status_types"] = OrderStatusType.choices
        return context
    
    
    
    
class AdminUsersDetailReviewView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/users/users-review.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        user_pk = self.kwargs.get("pk")
        queryset = ReviewModel.objects.filter(user_id=user_pk)

        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(product__title__icontains=search_q)

        if status := self.request.GET.get("status"):
            queryset = queryset.filter(status=status)

        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["status_types"] = ReviewStatusType.choices
        return context
    
    
    
class AdminUsersDetailChatView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    model = ChatRoom
    template_name = "dashboard/admin/users/users-chat.html"
    context_object_name = "object_list"
    paginate_by = 20  # اگر لازم داری صفحه‌بندی هم اضافه کن

    def get_queryset(self):
        user_pk = self.kwargs.get("pk")
        return ChatRoom.objects.filter(customer_id=user_pk)
