from django.views.generic import ListView,DetailView,UpdateView,CreateView,FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...permissions import HasAdminAccessPermission
from django.urls import reverse,reverse_lazy

from ...admin.forms import *
from django.core.exceptions import FieldError
from ....order.models import OrderModel,OrderStatusType
from ....payment.models import PayemntType,PaymentModel


class AdminPersonPayListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/person_pay/person-pay-list.html"
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size',self.paginate_by)

    def get_queryset(self):
        queryset = OrderModel.objects.filter(payment__payemnt_type=PayemntType.person.value)
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
    
    
    
class AdminPersonPayCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    model = PaymentModel
    form_class = InPersonPaymentForm
    template_name = "dashboard/admin/person_pay/person-pay-create.html"
    success_url = reverse_lazy("dashboard:person-pay-list")  # یا هر آدرس مناسب دیگر

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "ثبت پرداخت حضوری"
        return context