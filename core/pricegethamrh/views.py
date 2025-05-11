from django.views.generic import View,TemplateView
from shop.models import ProductModel,ProductColorInventory,Color
from .scripts import extract_product_data
from pricegethamrh.models import PriceGetHamrh

# Create your views here.
class GetColorAndPrice(TemplateView):
    template_name = "pricegethamrh/getcolor.html"
    
    def get_context_data(self, **kwargs):
        products = PriceGetHamrh.objects.filter(product__id=167)
        product = products.first().product
        extra = extract_product_data(products.first().url)
        
        colors = []
        for key, value in extra.items():
            color_title = value.get('color')
            if not color_title:
                continue

            color, _ = Color.objects.get_or_create(title=color_title)

            # قیمت با اولویت price → old_price → 0
            try:
                raw_price = int(value.get('price') or value.get('old_price') or 0)
            except (TypeError, ValueError):
                raw_price = 0

            # کم کردن 9.090909٪
            discounted_price = int(raw_price * 10 / 11)
            discounted_price = discounted_price+((discounted_price * 2.999) / 100)

            try:
                discount = int(0)
            except (TypeError, ValueError):
                discount = 0

            pci, created = ProductColorInventory.objects.get_or_create(
                product=product,
                color=color,
                defaults={
                    'price': discounted_price,
                    'discount_percent': discount
                }
            )

            if not created:
                pci.price = discounted_price
                pci.discount_percent = discount
                pci.save()

            colors.append(color)

        context = super().get_context_data(**kwargs)
        context['extras'] = extra
        context['products'] = products
        context['colors'] = colors
        return context

    
