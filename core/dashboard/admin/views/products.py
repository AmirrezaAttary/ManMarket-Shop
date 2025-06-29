from django.views.generic import (
    View,
    UpdateView,
    ListView,
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
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from shop.models import ProductModel, ProductCategoryModel, ProductImageModel
from django.core.exceptions import FieldError
from pricegethamrh.models import PriceGetHamrh
from getspecification.models import PriceSpecification



class AdminProductListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products/product-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = ProductModel.objects.all()
        
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get("category_id"):
            queryset = queryset.filter(category__id=category_id)
        if brand_id := self.request.GET.get("brand_id"):
            queryset = queryset.filter(brand__id=brand_id)
        if min_price := self.request.GET.get("min_price"):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.request.GET.get("max_price"):
            queryset = queryset.filter(price__lte=max_price)

        # 🆕 فیلتر وضعیت انتشار
        if status := self.request.GET.get("status"):
            try:
                status = int(status)
                if status in dict(ProductStatusType.choices):
                    queryset = queryset.filter(status=status)
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
        context["categories"] = ProductCategoryModel.objects.all()
        context["brands"] = Brand.objects.all()
        context["price_get_color_product_ids"] = PriceGetHamrh.objects.values_list('product_id', flat=True)
        context["specification_get_color_product_ids"] = PriceSpecification.objects.values_list('product_id', flat=True)

        # 🆕 اضافه کردن گزینه‌های فیلتر وضعیت به context
        context["status_choices"] = ProductStatusType.choices
        context["current_status_filter"] = self.request.GET.get("status")
        return context



class AdminProductCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/products/product-create.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm
    success_message = "ایجاد محصول با موفقیت انجام شد"

    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        return redirect(reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": form.instance.pk}))
        

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-list")


class AdminProductEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/products/product-edit.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm
    success_message = "ویرایش محصول با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": self.get_object().pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object  # محصولی که در حال ویرایش آن هستیم

        context["image_form"] = ProductImageForm(product=product)  # این خط اصلاح شد
        context["color_inventory_form"] = ProductColorInventoryForm()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.product_images.prefetch_related()
        return obj



class AdminProductDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/products/product-delete.html"
    queryset = ProductModel.objects.all()
    success_url = reverse_lazy("dashboard:admin:product-list")
    success_message = "حذف محصول با موفقیت انجام شد"
    
    
    
class AdminProductAddImageView(LoginRequiredMixin, HasAdminAccessPermission, View):
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(ProductModel, pk=self.kwargs.get('pk'))
        color_id = request.POST.get('color')  # فیلد رنگ
        files = request.FILES.getlist('files')  # گرفتن همه فایل‌ها

        if not files:
            messages.error(request, 'لطفاً حداقل یک تصویر انتخاب کنید.')
            return redirect(self.get_success_url())

        for file in files:
            ProductImageModel.objects.create(
                product=product,
                color_id=color_id,
                file=file
            )

        messages.success(request, 'تصاویر با موفقیت آپلود شدند.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})


class AdminProductRemoveImageView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    http_method_names = ["post"]
    success_message = "تصویر مورد نظر با موفقیت حذف شد"

    def get_queryset(self):
        return ProductImageModel.objects.filter(product__id=self.kwargs.get('pk'))
    
    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs.get('image_id'))

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})

    def form_invalid(self, form):
        messages.error(
            self.request, 'اشکالی در حذف تصویر رخ داد لطفا مجدد امتحان نمایید')
        return redirect(reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')}))




class AdminProductChangeColorImageView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    model = ProductImageModel
    form_class = ProductImageColorForm
    http_method_names = ["post"]
    success_message = "رنگ تصویر با موفقیت تغییر کرد"

    def get_queryset(self):
        return ProductImageModel.objects.filter(product__id=self.kwargs.get('pk'))
    
    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs.get('image_id'))

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})

    def form_invalid(self, form):
        messages.error(self.request, 'اشکالی در تغییر رنگ تصویر رخ داد. لطفا مجدد امتحان کنید.')
        return redirect(self.get_success_url())