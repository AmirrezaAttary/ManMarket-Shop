from django.views import View
from django.http import HttpResponseRedirect

from shop.models import  ProductColorInventory, Color
from .scripts import extract_product_data, get_kasrapars_product_data
from pricegethamrh.models import PriceGetHamrh
from django.urls import reverse
from .tasks import update_all_hamrah_products
from django.contrib import messages  
from django.shortcuts import redirect
import math


class GetColorAndPrice(View):

    def post(self, request, *args, **kwargs):
        return self.handle_request(request)

    def get(self, request, *args, **kwargs):
        return self.handle_request(request)

    def round_up_to_thousand(self, price):
        return math.ceil(price / 1000) * 1000

    def process_data(self, product, data, profit):
        existing_pcis = ProductColorInventory.objects.filter(product=product)
        existing_colors = {pci.color.title: pci for pci in existing_pcis}
        seen_colors = set()

        for key, value in data.items():
            color_title = value.get('color')
            color_code = value.get('color_code', '#ffffff')

            if not color_title:
                continue

            seen_colors.add(color_title)

            # ایجاد یا گرفتن رنگ
            color, created = Color.objects.get_or_create(title=color_title)

            # به‌روزرسانی hex_color در مدل Color
            if created or color.hex_color != color_code:
                color.hex_color = color_code
                color.save()

            try:
                raw_price = int(value.get('price') or value.get('old_price') or 0)
            except (TypeError, ValueError):
                raw_price = 0

            discounted_price = int(raw_price * profit) / 100
            discounted_price += raw_price

            final_price = self.round_up_to_thousand(discounted_price)
            discount = 0

            pci, created = ProductColorInventory.objects.get_or_create(
                product=product,
                color=color,
                defaults={
                    'price': final_price,
                    'discount_percent': discount,
                    'hex_color': color_code,
                    'stock': value.get('quantity', 0)
                }
            )

            if not created:
                pci.price = final_price
                pci.discount_percent = discount
                pci.hex_color = color_code
                pci.stock = value.get('quantity', 0)
                pci.save()

        for color_title, pci in existing_colors.items():
            if color_title not in seen_colors:
                pci.price = 0
                pci.stock = 0
                pci.save()


    def handle_request(self, request):
        product_id = self.kwargs.get("pk")
        products = PriceGetHamrh.objects.filter(product__id=product_id)

        if not products.exists():
            return HttpResponseRedirect(reverse("product_list"))

        for p in products:
            product = p.product

            combined_data = {}

            # بررسی و پردازش URL سایت همراه‌تل
            if p.url:
                extra_data = extract_product_data(p.url)
                if isinstance(extra_data, dict):
                    combined_data.update(extra_data)

            # بررسی و پردازش URL سایت کسری‌پارس
            if p.url_kasra:
                kasra_data = get_kasrapars_product_data(p.url_kasra)
                if isinstance(kasra_data, dict):
                    combined_data.update(kasra_data)

            # فقط یک بار پردازش داده‌های ترکیب‌شده
            self.process_data(product, combined_data, p.profit)

        return HttpResponseRedirect(self.get_success_url())


    def get_success_url(self):
        return reverse("dashboard:admin:product-edit", kwargs={"pk": self.kwargs.get("pk")})
    
    
class UpdateAllHamrahProductsView(View):
    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.INFO, 'در حال آپدیت رنگ وقیمت محصولات ...')
        update_all_hamrah_products.delay()
        return redirect(reverse("dashboard:admin:colors-list"))