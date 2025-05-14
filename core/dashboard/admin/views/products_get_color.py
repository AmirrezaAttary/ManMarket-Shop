from django.views.generic import (
    View,
    TemplateView,
    UpdateView,
    ListView,
    DeleteView,
    CreateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import PriceGetHamrhForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import FieldError
from pricegethamrh.models import PriceGetHamrh
from django.shortcuts import get_object_or_404



class AdminGetColorListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products-get-color/color-list.html"
    paginate_by = 10
    model = PriceGetHamrh.objects.all()

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = PriceGetHamrh.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context

class AdminGetColorCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/products-get-color/product-color-create.html"
    form_class = PriceGetHamrhForm
    model = PriceGetHamrh

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:colors-list')
    
class AdminGetColorDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/products-get-color/product-color-delete.html"
    queryset = PriceGetHamrh.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:colors-list')
    
class AdminGetColorEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/products-get-color/product-color-edit.html"
    queryset = PriceGetHamrh.objects.all()
    form_class = PriceGetHamrhForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"
    
    

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:colors-edit", kwargs={"pk": self.kwargs['pk']})