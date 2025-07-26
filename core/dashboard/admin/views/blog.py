from django.views.generic import (
    UpdateView,
    ListView,
    DeleteView,
    CreateView,
    FormView
)

from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import BlogPostForm,BlogPostProductForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy,reverse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import FieldError
from blog.models import Post,Category,PostProduct



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
    
  
class AdminBlogCreateView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    template_name = "dashboard/admin/blog/blog-create.html"
    form_class = BlogPostForm
    model = Post

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:blog-list')
    
    
  
class AdminBlogDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/blog/blog-delete.html"
    queryset = Post.objects.all()
    success_message = "حذف رنگ با موفقیت انجام شد"
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:blog-list')
    
  
class AdminBlogEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/blog/blog-edit.html"
    queryset = Post.objects.all()
    form_class = BlogPostForm
    success_message = "ویرایش رنگ با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:blog-edit", kwargs={"pk": self.kwargs['pk']})
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_product'] = BlogPostProductForm
        return context
    
class AdminBlogAddProduct(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, FormView):
    template_name = 'dashboard/admin/blog/add_product.html'
    form_class = BlogPostProductForm
    success_message = "محصول با موفقیت به پست اضافه شد."

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        product = form.cleaned_data['product']
        PostProduct.objects.get_or_create(post=self.post_instance, product=product)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("dashboard:admin:blog-edit", kwargs={"pk": self.post_instance.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'brand_slug': self.request.GET.get('brand'),
            'category_slug': self.request.GET.get('category'),
            'q': self.request.GET.get('q'),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_instance  # برای قالب همچنان post بفرست
        return context
