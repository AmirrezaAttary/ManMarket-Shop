from django.core.management.base import BaseCommand
from ...models import PriceGetHamrh
from ...scripts import extract_product_data, get_kasrapars_product_data
from ....shop.models import ProductColorInventory, Color
import math
import traceback


def round_up_to_thousand(price):
    return math.ceil(price / 1000) * 1000


def reset_product_inventory(product):
    ProductColorInventory.objects.filter(product=product).update(
        final_price=0,
        price=0,
        stock=0,
        discount_percent=0
    )


def process_data(product, variants, profit):
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

        final_price = (
            round_up_to_thousand(raw_price + (raw_price * profit / 100))
            if raw_price else 0
        )

        pci, created = ProductColorInventory.objects.get_or_create(
            product=product,
            color=color,
            defaults={
                "price": final_price,
                "final_price": final_price,
                "discount_percent": 0,
                "hex_color": color_code,
                "stock": item.get("quantity", 0),
            }
        )

        if not created:
            price_changed = pci.price != final_price
            pci.price = final_price
            pci.stock = item.get("quantity", 0)
            pci.hex_color = color_code
            pci.discount_percent = 0

            if price_changed:
                pci.final_price = final_price

            pci.save()

    for color_title, pci in existing_colors.items():
        if color_title not in seen_colors:
            pci.price = 0
            pci.stock = 0
            pci.save()


class Command(BaseCommand):
    help = "Update all Hamrah products prices and inventory"

    def handle(self, *args, **kwargs):
        self.stdout.write("شروع آپدیت محصولات...")

        items = PriceGetHamrh.objects.select_related("product").all()

        for item in items:
            product = item.product
            if not product:
                continue

            try:
                combined_variants = []

                if item.url:
                    hamrah_data = extract_product_data(item.url)
                    if isinstance(hamrah_data, list):
                        combined_variants.extend(hamrah_data)

                if item.url_kasra:
                    kasra_data = get_kasrapars_product_data(item.url_kasra)
                    if isinstance(kasra_data, list):
                        combined_variants.extend(kasra_data)

                if combined_variants:
                    process_data(product, combined_variants, item.profit)
                else:
                    reset_product_inventory(product)

            except Exception:
                traceback.print_exc()
                reset_product_inventory(product)

        self.stdout.write(self.style.SUCCESS("آپدیت کامل شد ✅"))
