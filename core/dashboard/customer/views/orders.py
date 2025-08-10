from django.views.generic import ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasCustomerAccessPermission
from django.shortcuts import redirect
from dashboard.customer.forms import *
from django.core.exceptions import FieldError
from order.models import OrderModel,OrderStatusType
import jdatetime

def to_jalali(date_obj):
    if not date_obj:
        return ""
    return jdatetime.datetime.fromgregorian(datetime=date_obj).strftime('%Y/%m/%d')


class CustomerOrderListView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    template_name = "dashboard/customer/orders/order-list.html"
    # paginate_by = 5
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size',self.paginate_by)

    def get_queryset(self):
        queryset = OrderModel.objects.filter(user=self.request.user)
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
    
    
    def get(self, request, *args, **kwargs):
        if "status" not in request.GET:
            return redirect(f"{request.path}?status={OrderStatusType.pending.value}")
        return super().get(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["status_types"] = OrderStatusType.choices  

        # تبدیل تاریخ به شمسی برای هر سفارش
        for order in context['object_list']:
            order.jalali_created_date = to_jalali(order.created_date)
            order.jalali_updated_date = to_jalali(order.updated_date)
        return context
 
  
class CustomerOrderDetailView(LoginRequiredMixin, HasCustomerAccessPermission, DetailView):
    template_name = "dashboard/customer/orders/order-detail.html"

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)

  
class CustomerOrderInvoiceView(LoginRequiredMixin, HasCustomerAccessPermission, DetailView):
    template_name = "dashboard/customer/orders/order-invoice.html"

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user,status=OrderStatusType.success.value)