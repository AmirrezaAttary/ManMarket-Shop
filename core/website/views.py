
from django.views.generic import TemplateView,CreateView,ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from website.forms import ContatctForm
from website.models import Contact
from shop.models import ProductModel,ProductStatusType
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
    
  
class GsmPayView(ListView):
    model = ProductModel
    template_name = 'website/gsmpay.html'

    def get_queryset(self):
        qs = ProductModel.objects.filter(
            status=ProductStatusType.publish.value,
            category__id=2,
            color_inventories__price__gt=0,
            color_inventories__stock__gt=0
        ).distinct().order_by('-avg_rate')[:4]

        for product in qs:
            product.priced_colors = product.color_inventories.filter(price__gt=0, stock__gt=0)
        return qs
