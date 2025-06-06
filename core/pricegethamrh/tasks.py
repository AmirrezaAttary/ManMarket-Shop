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
            print(f"✅ شروع پردازش محصول: {item.product.id} - URL: {item.url}")
            product = item.product
            if not product:
                continue

            print(f"🔄 پردازش: {product.id} | {item.url}")

            extra = extract_product_data(item.url)
            print(f"📦 نتیجه extra: {extra}")
            if not extra:
                print(f"❌ extra خالی است: {item.url}")
                print(f"⚠️ هیچ اطلاعاتی برای {item.url} دریافت نشد.")
                continue

            for key, value in extra.items():
                print(f"🎨 پردازش رنگ: {value.get('color')}, قیمت: {value.get('price')}")
                color_title = value.get('color')
                if not color_title:
                    continue

                color, _ = Color.objects.get_or_create(title=color_title)

                try:
                    raw_price = int(value.get('price') or 0)
                except (TypeError, ValueError):
                    raw_price = 0

                discounted_price = int(raw_price * 10 / 11)
                discounted_price += (discounted_price * 2.999) / 100
                color = color.strip()

                pci, created = ProductColorInventory.objects.get_or_create(
                    product=product,
                    color=color,
                    defaults={
                        'price': discounted_price,
                        'discount_percent': 0
                    }
                )

                if not created:
                    pci.price = discounted_price
                    pci.discount_percent = 0
                    pci.save()

        r.set("hamrah_update_status", "done", ex=300)

    except Exception as e:
        import traceback
        traceback.print_exc()  # چاپ ارور کامل در لاگ
        r.set("hamrah_update_status", f"error: {str(e)}", ex=300)
