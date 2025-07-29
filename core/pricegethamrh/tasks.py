from celery import shared_task
import redis
import math
from shop.models import ProductColorInventory, Color
from pricegethamrh.models import PriceGetHamrh
from .scripts import extract_product_data, get_kasrapars_product_data

def round_up_to_thousand(price):
    return math.ceil(price / 1000) * 1000

def process_data(product, data, source_name=""):
    for key, value in data.items():
        color_title = value.get('color')
        if not color_title:
            print(f"⚠️ رنگی برای variant {key} از {source_name} یافت نشد.")
            continue

        color, _ = Color.objects.get_or_create(title=color_title)

        try:
            raw_price = int(value.get('price') or 0)
        except (TypeError, ValueError):
            raw_price = 0

        discounted_price = int(raw_price * 2) / 100 + raw_price
        final_price = round_up_to_thousand(discounted_price)

        color_code = value.get('color_code', '#ffffff')
        pci, created = ProductColorInventory.objects.get_or_create(
            product=product,
            color=color,
            defaults={
                'price': final_price,
                'discount_percent': 0,
                'hex_color': color_code,
                'stock': value.get('quantity', 0)
            }
        )

        if not created:
            pci.price = final_price
            pci.discount_percent = 0
            pci.stock = value.get('quantity', 0)
            pci.hex_color = color_code
            pci.save(force_update=True)
            print(f"✅ [ویرایش] {product.title} | رنگ: {color_title} | منبع: {source_name} | قیمت: {final_price}")
        else:
            print(f"🆕 [جدید] {product.title} | رنگ: {color_title} | منبع: {source_name} | قیمت: {final_price}")


@shared_task
def update_all_hamrah_products():
    r = redis.Redis(host='redis', port=6379, db=2)
    try:
        products = PriceGetHamrh.objects.select_related('product').all()

        for item in products:
            product = item.product
            if not product:
                print(f"⚠️ محصولی برای رکورد {item.id} یافت نشد.")
                continue

            print(f"🔄 پردازش محصول: {product.id} | {product.title}")

            try:
                # ✅ پردازش از سایت همراه‌تل
                if item.url:
                    print(f"➡️ دریافت از hamrahtel: {item.url}")
                    extra = extract_product_data(item.url)
                    if isinstance(extra, dict) and extra:
                        process_data(product, extra, source_name="hamrahtel")
                    else:
                        print(f"⚠️ داده معتبری از hamrahtel دریافت نشد.")

                # ✅ پردازش از سایت کسری‌پارس
                if item.url_kasra:
                    print(f"➡️ دریافت از kasrapars: {item.url_kasra}")
                    extra_kasra = get_kasrapars_product_data(item.url_kasra)
                    if isinstance(extra_kasra, dict) and extra_kasra:
                        process_data(product, extra_kasra, source_name="kasrapars")
                    else:
                        print(f"⚠️ داده معتبری از kasrapars دریافت نشد.")

            except Exception as e:
                print(f"❌ خطا در پردازش محصول {product.title}")
                import traceback
                traceback.print_exc()
                ProductColorInventory.objects.filter(product=product).update(price=0)
                r.set("hamrah_update_status", f"error: General error for {product.title}", ex=300)
                continue

        r.set("hamrah_update_status", "done", ex=300)
        print("✅ بروزرسانی کامل انجام شد.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        r.set("hamrah_update_status", f"error: {str(e)}", ex=300)
        print(f"❌ خطای کلی: {e}")
