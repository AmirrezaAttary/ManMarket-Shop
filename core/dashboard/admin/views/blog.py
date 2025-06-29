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
from dashboard.admin.forms import BlogPostForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import FieldError
from blog.models import Post,Category


@method_decorator(cache_page(60 * 15), name='dispatch')
class AdminBlogListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/blog/blog-list.html"
    paginate_by = 10
    model = Post.objects.all()

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = Post.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get("category_id"):
            queryset = queryset.filter(category__id=category_id)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["categories"] = Category.objects.all()
        return context
    
@method_decorator(cache_page(60 * 15), name='dispatch')    
class AdminBlogCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/blog/blog-create.html"
    form_class = BlogPostForm
    model = Post

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:blog-list')
    
    
@method_decorator(cache_page(60 * 15), name='dispatch')    
class AdminBlogDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/blog/blog-delete.html"
    queryset = Post.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:blog-list')
    
@method_decorator(cache_page(60 * 15), name='dispatch')    
class AdminBlogEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/blog/blog-edit.html"
    queryset = Post.objects.all()
    form_class = BlogPostForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:blog-edit", kwargs={"pk": self.kwargs['pk']})