from django.views.generic import (
    UpdateView,
    DeleteView,
    CreateView
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from shop.models import ProductModel,ProductColorInventory


@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminProductAddColorView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/products-color/product-color-create.html"
    form_class = ProductColorInventoryForm
    model = ProductColorInventory
    queryset = ProductColorInventory.objects.all()

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = ProductModel.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = ProductModel.objects.get(pk=self.kwargs.get('pk'))
        return kwargs

    def form_valid(self, form):
        product = ProductModel.objects.get(pk=self.kwargs.get('pk'))
        color = form.cleaned_data['color']

        # بررسی وجود رنگ تکراری برای محصول
        if ProductColorInventory.objects.filter(product=product, color=color).exists():
            messages.error(self.request, 'این رنگ قبلاً برای این محصول ثبت شده است.')
            return redirect(self.get_success_url())

        form.instance.product = product

        messages.success(self.request, 'رنگ جدید با موفقیت ثبت شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'اشکالی در ثبت رنگ رخ داد. لطفاً مجدداً تلاش کنید.')
        return redirect(self.get_success_url())


@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminProductEditColorView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/products-color/product-color-edit.html"
    queryset = ProductColorInventory.objects.all()
    form_class = ProductColorInventoryForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": self.kwargs['prduct_pk']})


@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminProductColorDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/products-color/product-color-delete.html"
    queryset = ProductColorInventory.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs['prduct_pk']})