from django.db import migrations

from app.review.utils import clean_review_text


def clean_existing_reviews(apps, schema_editor):
    """نظرات قدیمیِ اسکرپ‌شده از دیجی‌کالا تگ HTML (<p>, <br>) داشتند؛ به متن ساده تبدیل می‌شوند."""
    Review = apps.get_model("review", "ReviewModel")
    for review in Review.objects.filter(description__contains="<").iterator():
        cleaned = clean_review_text(review.description)
        if cleaned != review.description:
            Review.objects.filter(pk=review.pk).update(description=cleaned)
    for review in Review.objects.filter(description__contains="&").iterator():
        cleaned = clean_review_text(review.description)
        if cleaned != review.description:
            Review.objects.filter(pk=review.pk).update(description=cleaned)


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0007_persian_labels"),
    ]

    operations = [
        migrations.RunPython(clean_existing_reviews, migrations.RunPython.noop),
    ]
