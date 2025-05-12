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
from dashboard.admin.forms import ProductCategoryModelForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import FieldError
from shop.models import ProductCategoryModel



class AdminProductCategoryListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products-category/category-list.html"
    paginate_by = 10
    model = ProductCategoryModel.objects.all()

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = ProductCategoryModel.objects.all()
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

class AdminProductCategoryCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/products-category/product-category-create.html"
    form_class = ProductCategoryModelForm
    model = ProductCategoryModel

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:category-list')
    
class AdminProductCategoryDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/products-category/product-category-delete.html"
    queryset = ProductCategoryModel.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:category-list')
    
class AdminProductCategoryEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/products-category/product-category-edit.html"
    queryset = ProductCategoryModel.objects.all()
    form_class = ProductCategoryModelForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:category-edit", kwargs={"pk": self.kwargs['pk']})