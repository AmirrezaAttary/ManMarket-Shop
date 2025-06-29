from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Create your views here.


class FaqView(TemplateView):
    template_name = 'faq/faq.html'

  
class CallWeView(TemplateView):
    template_name = 'faq/call-we.html'

  
class RulesView(TemplateView):
    template_name = 'faq/rules.html'

  
class TargetView(TemplateView):
    template_name = 'faq/target.html'

  
class ManOneSeenView(TemplateView):
    template_name = 'faq/man-one-seen.html'
    