# views.py
from django.views.generic import ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from ....website.models import Contact



class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'dashboard/admin/contact/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 12  # ← تعداد آیتم در هر صفحه


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'dashboard/admin/contact/contact_detail.html'
    context_object_name = 'contact'
    

  
class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    template_name = 'dashboard/admin/contact/contact_confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin:contact-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'پیام با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)


# class ContactDeleteView(LoginRequiredMixin, View):
#     def post(self, request, *args, **kwargs):
#         contact = get_object_or_404(Contact, pk=kwargs.get("pk"))
#         contact.delete()
#         messages.success(request, 'پیام با موفقیت حذف شد.')
#         return redirect(reverse_lazy('dashboard:admin:contact-list'))

