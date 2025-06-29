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
from dashboard.admin.forms import BlogCategoryModelForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import FieldError
from blog.models import Category


@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminBlogCategoryListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/blog-category/category-list.html"
    paginate_by = 10
    model = Category.objects.all()

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = Category.objects.all()
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
class AdminBlogCategoryCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/blog-category/blog-category-create.html"
    form_class = BlogCategoryModelForm
    model = Category

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:blog-category-list')


@method_decorator(cache_page(60 * 15), name='dispatch')    
class AdminBlogCategoryDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/blog-category/blog-category-delete.html"
    queryset = Category.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:blog-category-list')
    
@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminBlogCategoryEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/blog-category/blog-category-edit.html"
    queryset = Category.objects.all()
    form_class = BlogCategoryModelForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:blog-category-edit", kwargs={"pk": self.kwargs['pk']})