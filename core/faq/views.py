from django.views.generic import TemplateView


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
    
class TasisView(TemplateView):
    template_name = 'faq/tasis.html'
    
    
class AsasView(TemplateView):
    template_name = 'faq/asas.html'
    
class AfzayeshView(TemplateView):
    template_name = 'faq/afzayesh.html'

