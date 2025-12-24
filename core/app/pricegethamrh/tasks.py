from celery import shared_task
import redis
import math
from ..shop.models import ProductColorInventory, Color
from .models import PriceGetHamrh
from .scripts import extract_product_data, get_kasrapars_product_data

def round_up_to_thousand(price):
    return math.ceil(price / 1000) * 1000

def reset_product_inventory(product):
    ProductColorInventory.objects.filter(product=product).update(
        final_price=0,
        price=0,
        stock=0,
        discount_percent=0
    )



def process_data(product, variants, profit, source_name=""):
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

        print(
            f"✅ {product.title} | {color_title} | {source_name} | {final_price}"
        )

    # رنگ‌های حذف‌شده
    for color_title, pci in existing_colors.items():
        if color_title not in seen_colors:
            pci.price = 0
            pci.stock = 0
            pci.save()


@shared_task
def update_all_hamrah_products():
    r = redis.Redis(host="redis", port=6379, db=2)

    try:
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

            except Exception as e:
                import traceback
                traceback.print_exc()
                reset_product_inventory(product)
                continue

    except Exception as e:
        import traceback
        traceback.print_exc()
        r.set("hamrah_update_status", f"error: {str(e)}", ex=300)
