# tasks.py
from celery import shared_task
import redis
from shop.models import ProductColorInventory, Color
from pricegethamrh.models import PriceGetHamrh
from .scripts import extract_product_data

@shared_task
def update_all_hamrah_products():
    r = redis.Redis(host='redis', port=6379, db=2)
    try:
        products = PriceGetHamrh.objects.select_related('product').all()

        for item in products:
            product = item.product
            if not product:
                continue

            extra = extract_product_data(item.url)
            if not extra:
                continue

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

        # فقط اگر همه چیز بدون خطا انجام شد:
        r.set("hamrah_update_status", "done", ex=300)

    except Exception as e:
        r.set("hamrah_update_status", f"error: {str(e)}", ex=300)
