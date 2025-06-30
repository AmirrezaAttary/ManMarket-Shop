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
                print(f"⚠️ محصولی مرتبط با {item.id} یافت نشد.")
                continue

            print(f"🔄 پردازش: {product.id} | {item.url}")

            try:
                extra = extract_product_data(item.url)

                # بررسی اعتبار خروجی
                if not extra or not isinstance(extra, dict):
                    print(f"⚠️ اطلاعات معتبر برای {item.url} دریافت نشد.")
                    continue

                for key, value in extra.items():
                    color_title = value.get('color')
                    if not color_title:
                        print(f"⚠️ رنگی برای variant {key} در {item.url} یافت نشد.")
                        continue

                    color, _ = Color.objects.get_or_create(title=color_title)

                    try:
                        raw_price = int(value.get('price') or 0)
                    except (TypeError, ValueError):
                        raw_price = 0

                    discounted_price = int(raw_price * 10 / 11)
                    discounted_price += int((discounted_price * 2.999) / 100)

                    pci, created = ProductColorInventory.objects.get_or_create(
                        product=product,
                        color=color,
                        defaults={
                            'price': discounted_price,
                            'discount_percent': 0,
                            'hex_color': value.get('color_code', '#ffffff')  # پیش‌فرض سفید
                        }
                    )

                    if not created:
                        pci.price = discounted_price
                        pci.discount_percent = 0
                        pci.save()
                        print(f"✅ قیمت بروزرسانی شد: {product.id} | رنگ: {color_title} | قیمت: {discounted_price}")
                    else:
                        print(f"🆕 موجودی جدید اضافه شد: {product.id} | رنگ: {color_title} | قیمت: {discounted_price}")

            except Exception as e:
                print(f"❌ خطا در پردازش محصول {product.id} | URL: {item.url}")
                import traceback
                traceback.print_exc()
                continue

        r.set("hamrah_update_status", "done", ex=300)
        print("✅ بروزرسانی همه محصولات همکار با موفقیت انجام شد.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        r.set("hamrah_update_status", f"error: {str(e)}", ex=300)
        print(f"❌ خطای کلی در task: {e}")
