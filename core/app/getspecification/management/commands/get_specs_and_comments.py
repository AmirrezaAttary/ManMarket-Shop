import datetime
import time
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import PriceSpecification
from ...scripts import getspecificationDigikala, getCommentsDigikala
from ....review.models import ReviewModel, ReviewStatusType
from ....shop.models import ProductSpecification


def save_specifications(product, url):
    """مشخصات فنی را می‌گیرد و ذخیره/آپدیت می‌کند. تعداد مشخصات ذخیره‌شده را برمی‌گرداند."""
    specs = getspecificationDigikala(url) or {}
    for key, value in specs.items():
        ProductSpecification.objects.update_or_create(
            product=product,
            name=str(key),
            defaults={"value": str(value)},
        )
    return len(specs)


def save_comments(product, url, number_comments):
    """
    نظرات را می‌گیرد و از همان ابتدا با وضعیت «تایید شده» ذخیره می‌کند.
    تعداد نظرات جدید را برمی‌گرداند.
    """
    comments = getCommentsDigikala(url=url, number_comments=number_comments)
    new_count = 0

    for comment in comments:
        created_at = comment.get("created_at") or timezone.now()
        if settings.USE_TZ and timezone.is_naive(created_at):
            created_at = timezone.make_aware(created_at, datetime.timezone.utc)

        # status فقط در defaults است تا اگر نظر قبلاً وجود داشت
        # (مثلاً ادمین ردش کرده بود) وضعیتش دست نخورد.
        # چون با create ساخته می‌شود، سیگنال میانگین امتیاز هم اجرا می‌شود.
        _, created = ReviewModel.objects.get_or_create(
            product=product,
            name=comment["name"],
            description=comment["description"],
            rate=comment["rate"],
            created_date=created_at,
            defaults={"status": ReviewStatusType.accepted.value},
        )
        if created:
            new_count += 1

    return new_count


class Command(BaseCommand):
    help = "دریافت مشخصات و نظرات محصولات از دیجی‌کالا (نظرات مستقیماً تایید‌شده ذخیره می‌شوند)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--product-id", type=int, nargs="+",
            help="فقط برای این محصولات اجرا شود (یک یا چند id)",
        )
        parser.add_argument("--skip-specs", action="store_true", help="مشخصات گرفته نشود")
        parser.add_argument("--skip-comments", action="store_true", help="نظرات گرفته نشود")
        parser.add_argument(
            "--sleep", type=float, default=1.0,
            help="مکث (ثانیه) بین هر محصول برای جلوگیری از بلاک شدن (پیش‌فرض ۱)",
        )

    def handle(self, *args, **options):
        items = PriceSpecification.objects.select_related("product").exclude(url__isnull=True).exclude(url="")
        items = items.filter(product__isnull=False)

        if options["product_id"]:
            items = items.filter(product_id__in=options["product_id"])

        total = items.count()
        if not total:
            self.stdout.write(self.style.WARNING("هیچ محصولی با لینک دیجی‌کالا پیدا نشد."))
            return

        self.stdout.write(f"شروع دریافت اطلاعات برای {total} محصول...")

        for index, item in enumerate(items, start=1):
            product = item.product
            line = f"[{index}/{total}] محصول {product.id}"

            try:
                if not options["skip_specs"]:
                    specs_count = save_specifications(product, item.url)
                    line += f" | مشخصات: {specs_count}"

                if not options["skip_comments"]:
                    new_comments = save_comments(product, item.url, item.number_comments or 10)
                    line += f" | نظر جدید (تایید‌شده): {new_comments}"

                self.stdout.write(self.style.SUCCESS(line + " ✅"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{line} ❌ {e}"))
                traceback.print_exc()

            if options["sleep"] and index < total:
                time.sleep(options["sleep"])

        self.stdout.write(self.style.SUCCESS("تمام شد ✅"))
