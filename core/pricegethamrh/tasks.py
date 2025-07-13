# tasks.py
from celery import shared_task
import redis
from shop.models import ProductColorInventory, Color
from pricegethamrh.models import PriceGetHamrh
from .scripts import extract_product_data
import math

def round_up_to_thousand(price):
    return math.ceil(price / 1000) * 1000

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

                    discounted_price = int(raw_price * 2 ) /100
                    discounted_price += raw_price
                    
                    final_price = round_up_to_thousand(discounted_price)
                    
                    color_code = value.get('color_code', '#ffffff')
                    pci, created = ProductColorInventory.objects.get_or_create(
                        product=product,
                        color=color,
                        defaults={
                            'price': final_price,
                            'discount_percent': 0,
                            'hex_color': color_code,  # پیش‌فرض سفید
                            'stock': value.get('quantity', 0)
                        }
                    )

                    if not created:
                        pci.price = final_price
                        pci.discount_percent = 0
                        pci.stock = value.get('quantity', 0)
                        pci.hex_color = color_code
                        pci.save()
                        print(f"✅ قیمت بروزرسانی شد: {product.title} | رنگ: {color_title} | قیمت: {final_price}")
                    else:
                        print(f"🆕 موجودی جدید اضافه شد: {product.title} | رنگ: {color_title} | قیمت: {final_price}")

            except Exception as e:
                print(f"❌ خطا در پردازش محصول {product.title} | URL: {item.url}")
                import traceback
                traceback.print_exc()
                ProductColorInventory.objects.filter(product=product).update(price=0)
                print(f"صفر شدن قیمت‌ها برای محصول: {product.title} به دلیل خطای عمومی.")
                r.set("hamrah_update_status", f"error: General error for {product.title}", ex=300)
                continue
            
        r.set("hamrah_update_status", "done", ex=300)
        print("✅ بروزرسانی همه محصولات همکار با موفقیت انجام شد.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        r.set("hamrah_update_status", f"error: {str(e)}", ex=300)
        print(f"❌ خطای کلی در task: {e}")
