from django.views import View
from django.http import HttpResponseRedirect
from shop.models import ProductModel, ProductColorInventory, Color
from .scripts import extract_product_data
from pricegethamrh.models import PriceGetHamrh
from django.urls import reverse
from django.http import JsonResponse
from .tasks import update_all_hamrah_products
from django.contrib import messages  
from django.shortcuts import redirect

class GetColorAndPrice(View):

    def post(self, request, *args, **kwargs):
        return self.handle_request(request)

    def get(self, request, *args, **kwargs):
        return self.handle_request(request)

    def handle_request(self, request):
        product_id = self.kwargs.get("pk")
        products = PriceGetHamrh.objects.filter(product__id=product_id)
        if not products.exists():
            # اگر محصول پیدا نشد، مثلاً به صفحه خطا یا لیست محصولات برگرد
            return HttpResponseRedirect(reverse("product_list"))

        product = products.first().product
        extra = extract_product_data(products.first().url)

        for key, value in extra.items():
            color_title = value.get('color')
            if not color_title:
                continue

            color, _ = Color.objects.get_or_create(title=color_title)

            try:
                raw_price = int(value.get('price') or value.get('old_price') or 0)
            except (TypeError, ValueError):
                raw_price = 0

            discounted_price = int(raw_price * 10 / 11)
            discounted_price += (discounted_price * 2.999) / 100

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

        # ✅ ریدایرکت به صفحه‌ای که می‌خوای
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        # مسیر دلخواه خودت رو جایگزین کن
        return reverse("dashboard:admin:product-edit", kwargs={"pk": self.kwargs.get("pk")})
    
    
class UpdateAllHamrahProductsView(View):
    def post(self, request, *args, **kwargs):
        update_all_hamrah_products.delay()
        messages.add_message(request, messages.INFO, 'در حال آپدیت رنگ وقیمت محصولات ...')
        return redirect(reverse("dashboard:admin:colors-list"))