from celery import shared_task
import time
from ..shop.models import ProductSpecification
from .models import PriceSpecification
from .scripts import getspecificationDigikala

@shared_task
def fetch_and_save_specifications(product_id):
    try:
        start_time = time.time()
        products = PriceSpecification.objects.filter(product__id=product_id)
        if not products.exists():
            return f"[{product_id}] ❌ Product not found"
        product = products.first().product
        extra = getspecificationDigikala(products.first().url)
        duration = time.time() - start_time
        if duration > 2:
            return f"[{product_id}] ⚠️ Took {duration:.2f}s — Skipped due to timeout"
        if extra:
            for key, value in extra.items():
                ProductSpecification.objects.update_or_create(
                    product=product,
                    name=str(key),
                    defaults={"value": str(value)}
                )
        return f"[{product_id}] ✅ Done in {duration:.2f}s"
    except Exception as e:
        return f"[{product_id}] ❌ Error: {str(e)}"

@shared_task
def all_specifications_updated(results):
    print("✅ همه مشخصات آپدیت شدند.")
    for result in results:
        print(result)
