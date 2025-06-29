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
from dashboard.admin.forms import PriceGetHamrhForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import FieldError
from pricegethamrh.models import PriceGetHamrh
import redis
from django.http import JsonResponse

def check_hamrah_status(request):
    r = redis.Redis(host='redis', port=6379, db=2)
    status = r.get("hamrah_update_status")
    if status:
        status = status.decode()
        if status == "done":
            r.delete("hamrah_update_status")
            return JsonResponse({"status": "done"})
        elif status.startswith("error:"):
            r.delete("hamrah_update_status")
            return JsonResponse({"status": "error", "message": status})
    return JsonResponse({"status": "pending"})


@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminGetColorListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products-get-color/color-list.html"
    paginate_by = 10
    model = PriceGetHamrh.objects.all()

    def get(self, request, *args, **kwargs):
        r = redis.Redis(host='redis', port=6379, db=2)
        status = r.get("hamrah_update_status")

        if status:
            status = status.decode()
            if status == "done":
                messages.success(request, "✅ قیمت و رنگ محصولات با موفقیت آپدیت شد.")
            elif status.startswith("error:"):
                messages.error(request, f"❌ خطا در آپدیت: {status}")
            r.delete("hamrah_update_status")

        return super().get(request, *args, **kwargs)  # ✅ بسیار مهم!

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

@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminGetColorCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/products-get-color/product-color-create.html"
    form_class = PriceGetHamrhForm
    model = PriceGetHamrh

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:colors-list')

@method_decorator(cache_page(60 * 15), name='dispatch')    
class AdminGetColorDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/products-get-color/product-color-delete.html"
    queryset = PriceGetHamrh.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:colors-list')

@method_decorator(cache_page(60 * 15), name='dispatch')    
class AdminGetColorEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/products-get-color/product-color-edit.html"
    queryset = PriceGetHamrh.objects.all()
    form_class = PriceGetHamrhForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"
    
    

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:colors-edit", kwargs={"pk": self.kwargs['pk']})