from django.views.generic import ListView,DetailView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...permissions import HasAdminAccessPermission
from django.urls import reverse

from ...admin.forms import *
from django.core.exceptions import FieldError
from ....order.models import OrderModel,OrderStatusType
from ....accounts.scripts import send_bulk_sms


class AdminOrderListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/orders/order-list.html"
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size',self.paginate_by)

    def get_queryset(self):
        queryset = OrderModel.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(id__icontains=search_q)
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
        context["status_types"] = OrderStatusType.choices
        return context
    
  
class AdminOrderDetailView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/orders/order-detail.html"

    def get_queryset(self):
        return OrderModel.objects.all()
    
    
from django.contrib import messages

class AdminOrderEditView(LoginRequiredMixin, HasAdminAccessPermission, UpdateView):
    template_name = "dashboard/admin/orders/order-edit.html"
    queryset = OrderModel.objects.all()
    form_class = OrederModelForm

    def form_valid(self, form):
        order: OrderModel = form.save(commit=False)
        old_status = self.get_object().status  # وضعیت قبلی
        new_status = form.cleaned_data.get("status")

        response = super().form_valid(form)  # ذخیره‌ی سفارش

        if old_status != new_status:
            self.send_status_sms(order, new_status)

        return response

    def send_status_sms(self, order, new_status):
        """ارسال پیامک متناسب با تغییر وضعیت سفارش"""
        status_messages = {
            OrderStatusType.pending: f"مشتری گرامی،\nسفارش شما {order.order_number}\nدر وضعیت «در حال پرداخت» است\nو تا ۳۰ دقیقه معتبر خواهد بود\nمـــن مـــارکـــت",
            OrderStatusType.awaiting: f"مشتری گرامی،\nسفارش شما {order.order_number} تأیید شد\nدر حال آماده‌سازی است.\nمـــن مـــارکـــت",
            OrderStatusType.success: f"مشتری گرامی،\nسفارش شما {order.order_number} تأیید شد\nدر حال آماده‌سازی است.\nمـــن مـــارکـــت",
            OrderStatusType.shipped: f"مشتری گرامی،\nسفارش شما {order.order_number} ارسال شد.\nکد رهگیری : {order.tracking_code or '---'}\nمـــن مـــارکـــت",
            OrderStatusType.deliverd: f"مشتری گرامی،\nسفارش شما {order.order_number}\nبا موفقیت تحویل شد.\nمـــن مـــارکـــت",
            OrderStatusType.failed: f"مشتری گرامی،\nسفارش شما {order.order_number} لغو شد.\nبرای اطلاعات بیشتر با پشتیبانی تماس بگیرید.\nمـــن مـــارکـــت",
        }

        message_text = status_messages.get(new_status)
        if message_text:
            user_phone = order.user.phone_number
            if user_phone:
                result = send_bulk_sms(message_text, [user_phone])
                if result.get("status") == 1:  # موفق
                    messages.success(self.request, f"پیامک وضعیت سفارش {order.id} با موفقیت ارسال شد ✅")
                else:
                    messages.error(self.request, f"خطا در ارسال پیامک برای سفارش {order.id}: {result.get('message')}")
            else:
                messages.warning(self.request, f"سفارش {order.id} شماره موبایل ثبت‌شده ندارد ❌")

    def get_success_url(self):
        return reverse("dashboard:admin:order-detail", kwargs={'pk': self.kwargs['pk']})


    
  
class AdminOrderInvoiceView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/orders/order-invoice.html"

    def get_queryset(self):
        return OrderModel.objects.filter(status=OrderStatusType.success.value)