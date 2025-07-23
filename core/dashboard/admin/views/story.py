from django.views.generic import UpdateView,ListView,CreateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from django.shortcuts import redirect

from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import FieldError
from website.models import Story,ReviewStatusType


class AdminStoryListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/storys/story-list.html"
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size',self.paginate_by)

    def get_queryset(self):
        queryset = Story.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q) | queryset.filter(id__iexact=search_q)
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
        context["status_types"] = ReviewStatusType.choices
        return context

  
class AdminStoryEditView(LoginRequiredMixin, HasAdminAccessPermission,SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/storys/story-edit.html"
    queryset = Story.objects.all()
    form_class = StoryForm
    success_message = "تغییرات با موفقیت اعمال شد"
    
    def get_success_url(self) -> str:
        return reverse_lazy("dashboard:admin:story-edit",kwargs={"pk":self.kwargs.get("pk")})
    
    
    
class AdminStoryCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/storys/story-create.html"
    queryset = Story.objects.all()
    form_class = StoryForm
    success_message = "ایجاد استوری با موفقیت انجام شد"

    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        return redirect(reverse_lazy("dashboard:admin:story-edit", kwargs={"pk": form.instance.pk}))
        

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:story-list")
    
    
class AdminStoryDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/storys/story-delete.html"
    queryset = Story.objects.all()
    success_url = reverse_lazy("dashboard:admin:story-list")
    success_message = "حذف استوری با موفقیت انجام شد"