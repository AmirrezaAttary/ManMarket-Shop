from django.views.generic import (
    UpdateView,
    ListView,
    DeleteView,
    CreateView
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import ColorModelForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import FieldError
from shop.models import Color


@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminColorListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/color/color-list.html"
    paginate_by = 10
    model = Color.objects.all()

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = Color.objects.all()
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

@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminColorCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/color/color-create.html"
    form_class = ColorModelForm
    model = Color

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:color-list')
    
@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminColorDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/color/color-delete.html"
    queryset = Color.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:color-list')

@method_decorator(cache_page(60 * 15), name='dispatch')    
class AdminColorEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/color/color-edit.html"
    queryset = Color.objects.all()
    form_class = ColorModelForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:color-edit", kwargs={"pk": self.kwargs['pk']})