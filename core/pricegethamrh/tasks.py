from celery import shared_task
import redis
import math
from shop.models import ProductColorInventory, Color
from pricegethamrh.models import PriceGetHamrh
from .scripts import extract_product_data, get_kasrapars_product_data

def round_up_to_thousand(price):
    return math.ceil(price / 1000) * 1000

def process_data(product, data, profit, source_name=""):
    existing_pcis = ProductColorInventory.objects.filter(product=product)
    existing_colors = {pci.color.title: pci for pci in existing_pcis}
    seen_colors = set()

    for key, value in data.items():
        color_title = value.get('color')
        if not color_title:
            print(f"⚠️ رنگی برای variant {key} از {source_name} یافت نشد.")
            continue

        seen_colors.add(color_title)

        color, created = Color.objects.get_or_create(title=color_title)
        color_code = value.get('color_code', '#ffffff')

        # آپدیت hex_color در مدل Color
        if created or color.hex_color != color_code:
            color.hex_color = color_code
            color.save()

        try:
            raw_price = int(value.get('price') or 0)
        except (TypeError, ValueError):
            raw_price = 0

        discounted_price = int(raw_price * profit) / 100 + raw_price
        final_price = round_up_to_thousand(discounted_price)

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

    for color_title, pci in existing_colors.items():
        if color_title not in seen_colors:
            pci.price = 0
            pci.stock = 0
            pci.save()
            print(f"🔁 [غیرفعال] {product.title} | رنگ: {color_title} | قیمت و موجودی صفر شد.")

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

            combined_data = {}

            try:
                if item.url:
                    print(f"➡️ دریافت از hamrahtel: {item.url}")
                    extra = extract_product_data(item.url)
                    if isinstance(extra, dict) and extra:
                        combined_data.update(extra)
                    else:
                        print(f"⚠️ داده معتبری از hamrahtel دریافت نشد.")

                if item.url_kasra:
                    print(f"➡️ دریافت از kasrapars: {item.url_kasra}")
                    extra_kasra = get_kasrapars_product_data(item.url_kasra)
                    if isinstance(extra_kasra, dict) and extra_kasra:
                        combined_data.update(extra_kasra)
                    else:
                        print(f"⚠️ داده معتبری از kasrapars دریافت نشد.")

                if combined_data:
                    process_data(product, combined_data, item.profit, source_name="merged")

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
