from django.views.generic import View,TemplateView
from shop.models import ProductModel,ProductColorInventory,Color
from .scripts import extract_product_data
from pricegethamrh.models import PriceGetHamrh

# Create your views here.
class GetColorAndPrice(TemplateView):
    template_name = "pricegethamrh/getcolor.html"
    
    def get_context_data(self, **kwargs):
        products = PriceGetHamrh.objects.filter(product__id=164)
        extra = extract_product_data(products.first().url)
        colors = []
        for key, value in extra.items():
            color = Color.objects.get_or_create(title = value['color'])
            colors.append(color)

        color_inventory = ProductColorInventory.objects.filter(product__id=products.first().product.id)
        context = super().get_context_data(**kwargs)
        context['extras'] = extra
        context['products'] = products
        context['colors'] = colors
        context['color_inventory'] = color_inventory
        return context
    
