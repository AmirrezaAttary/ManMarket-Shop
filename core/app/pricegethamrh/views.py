from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages  
from django.shortcuts import redirect
import math

from ..shop.models import  ProductColorInventory, Color
from .scripts import extract_product_data, get_kasrapars_product_data
from ..pricegethamrh.models import PriceGetHamrh
from .tasks import update_all_hamrah_products



class GetColorAndPrice(View):

    def post(self, request, *args, **kwargs):
        return self.handle_request(request)

    def get(self, request, *args, **kwargs):
        return self.handle_request(request)

    def round_up_to_thousand(self, price):
        return math.ceil(price / 1000) * 1000

    # 🔹 صفر کردن کامل محصول
    def reset_product_inventory(self, product):
        ProductColorInventory.objects.filter(product=product).update(
            price=0,
            stock=0,
            discount_percent=0
        )

    def process_data(self, product, variants, profit):
        """
        variants => list of dicts
        """
        existing_pcis = ProductColorInventory.objects.filter(product=product)
        existing_colors = {pci.color.title: pci for pci in existing_pcis}
        seen_colors = set()

        for item in variants:
            color_title = item.get("color")
            color_code = item.get("color_code") or "#ffffff"

            if not color_title:
                continue

            seen_colors.add(color_title)

            color, created = Color.objects.get_or_create(title=color_title)

            if created or color.hex_color != color_code:
                color.hex_color = color_code
                color.save(update_fields=["hex_color"])

            try:
                raw_price = int(item.get("price") or 0)
            except (TypeError, ValueError):
                raw_price = 0

            discounted_price = raw_price + (raw_price * profit / 100)
            final_price = self.round_up_to_thousand(discounted_price) if raw_price else 0

            pci, created = ProductColorInventory.objects.get_or_create(
                product=product,
                color=color,
                defaults={
                    "price": final_price,
                    "discount_percent": 0,
                    "hex_color": color_code,
                    "stock": item.get("quantity", 0),
                }
            )

            if not created:
                pci.price = final_price
                pci.discount_percent = 0
                pci.hex_color = color_code
                pci.stock = item.get("quantity", 0)
                pci.save()

        # 🔻 رنگ‌هایی که دیگه وجود ندارن
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
            combined_variants = []

            # ✅ همراه‌تل
            if p.url:
                hamrah_data = extract_product_data(p.url)

                if hamrah_data is None:
                    # ❗ اگر None بود → صفر کن
                    self.reset_product_inventory(product)
                    continue

                if isinstance(hamrah_data, list):
                    combined_variants.extend(hamrah_data)

            # ✅ کسرا بعداً
            if p.url_kasra:
                kasra_data = get_kasrapars_product_data(p.url_kasra)

                if kasra_data is None:
                    self.reset_product_inventory(product)
                    continue

                if isinstance(kasra_data, list):
                    combined_variants.extend(kasra_data)

            if combined_variants:
                self.process_data(product, combined_variants, p.profit)
            else:
                self.reset_product_inventory(product)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "dashboard:admin:product-edit",
            kwargs={"pk": self.kwargs.get("pk")}
        )  
    
class UpdateAllHamrahProductsView(View):
    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.INFO, 'در حال آپدیت رنگ وقیمت محصولات ...')
        update_all_hamrah_products.delay()
        return redirect(reverse("dashboard:admin:colors-list"))