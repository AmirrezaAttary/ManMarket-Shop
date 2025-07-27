
from django.views.generic import TemplateView,CreateView
from django.contrib.messages.views import SuccessMessageMixin
from website.forms import ContatctForm
from website.models import Contact
from django.urls import reverse_lazy
# Create your views here.


class IndexView(TemplateView):
    template_name = 'website/index.html'
    
  
class ContactView(SuccessMessageMixin,CreateView):
    template_name = 'website/contact.html'
    form_class = ContatctForm
    model = Contact
    success_url = reverse_lazy('website:contact')
    success_message = 'درخواست شما ثبت شد\nبزودی با شما تماس گرفته میشود'
    
    
  
class AboutView(TemplateView):
    template_name = 'faq/man-one-seen.html'
    
  
class CollectionView(TemplateView):
    template_name = 'website/collection.html'