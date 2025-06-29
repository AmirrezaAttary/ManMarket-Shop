from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView,CreateView
from django.contrib.messages.views import SuccessMessageMixin
from website.forms import ContatctForm
from website.models import Contact
from django.urls import reverse_lazy
# Create your views here.

@method_decorator(cache_page(60 * 15), name='dispatch')
class IndexView(TemplateView):
    template_name = 'website/index.html'
    
@method_decorator(cache_page(60 * 15), name='dispatch')    
class ContactView(SuccessMessageMixin,CreateView):
    template_name = 'website/contact.html'
    form_class = ContatctForm
    model = Contact
    success_url = reverse_lazy('website:contact')
    success_message = 'درخواست شما ثبت شد\nبزودی با شما تماس گرفته میشود'
    
    
@method_decorator(cache_page(60 * 15), name='dispatch')    
class AboutView(TemplateView):
    template_name = 'website/about.html'
    
@method_decorator(cache_page(60 * 15), name='dispatch')    
class CollectionView(TemplateView):
    template_name = 'website/collection.html'