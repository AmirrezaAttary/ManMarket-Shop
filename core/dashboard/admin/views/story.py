from django.views.generic import UpdateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission

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
            queryset = queryset.filter(title__icontains=search_q)
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