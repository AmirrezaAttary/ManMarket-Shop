from threading import Lock
from django.utils import timezone
from .scripts import getCommentsDigikala
from ..review.models import ReviewModel

db_lock = Lock()

# تابع پردازش کامنت‌ها
def process_comments(product_id, number_comments, url):
    comments = getCommentsDigikala(url=url, number_comments=number_comments)
    for comment in comments:
        created_at = comment['created_at']
        # فقط اگر naive است، به UTC aware تبدیل می‌کنیم
        if created_at.tzinfo is None:
            created_at = timezone.make_aware(created_at, timezone.utc)

        with db_lock:
            ReviewModel.objects.get_or_create(
                product_id=product_id,
                name=comment['name'],
                description=comment['description'],
                rate=comment['rate'],
                created_date=created_at,
            )