import json
from pathlib import Path

from django.core.management.base import BaseCommand

from ...models import FAQ, FAQCategory, SiteSetting

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "default_faq.json"

# همان مقادیری که قبلاً در فوتر و صفحه‌ی تماس فرانت ثابت نوشته شده بود
SITE_DEFAULTS = {
    "site_name": "من مارکت",
    "instagram": "https://www.instagram.com/manmarket_ir/",
    "telegram": "https://t.me/Manmarket_ir",
    "whatsapp": "https://wa.me/message/MARSJJ37Q77WN1",
}


class Command(BaseCommand):
    help = (
        "سوالات متداول فعلی سایت و اطلاعات شبکه‌های اجتماعی را یک بار در دیتابیس می‌ریزد تا از پنل قابل ویرایش شوند. "
        "چند بار اجرا کردنش امن است: موارد موجود دوباره ساخته یا بازنویسی نمی‌شوند."
    )

    def handle(self, *args, **options):
        category_by_key = {c.name.replace("_", "-"): c.value for c in FAQCategory}
        created = 0
        for order, item in enumerate(json.loads(FIXTURE.read_text(encoding="utf-8")), start=1):
            _, was_created = FAQ.objects.get_or_create(
                question=item["question"],
                defaults={
                    "answer": item["answer"],
                    "category": category_by_key[item["category_key"]],
                    "sort_order": order,
                },
            )
            created += int(was_created)

        setting = SiteSetting.load()
        filled = []
        for field, value in SITE_DEFAULTS.items():
            if not getattr(setting, field):
                setattr(setting, field, value)
                filled.append(field)
        if filled:
            setting.save()

        self.stdout.write(self.style.SUCCESS(
            f"{created} سوال متداول اضافه شد؛ تنظیمات سایت: {', '.join(filled) or 'بدون تغییر'}"
        ))
