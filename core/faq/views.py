from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Create your views here.

@method_decorator(cache_page(60 * 15), name='dispatch')
class FaqView(TemplateView):
    template_name = 'faq/faq.html'

@method_decorator(cache_page(60 * 15), name='dispatch')    
class CallWeView(TemplateView):
    template_name = 'faq/call-we.html'

@method_decorator(cache_page(60 * 15), name='dispatch')    
class RulesView(TemplateView):
    template_name = 'faq/rules.html'

@method_decorator(cache_page(60 * 15), name='dispatch')    
class TargetView(TemplateView):
    template_name = 'faq/target.html'

@method_decorator(cache_page(60 * 15), name='dispatch')    
class ManOneSeenView(TemplateView):
    template_name = 'faq/man-one-seen.html'
    