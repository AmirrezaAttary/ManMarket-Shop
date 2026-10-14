from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bwdk", "0002_rename_bwdk_bwdkord_status_8d95a2_idx_bwdk_bwdkor_status_a6dc8d_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="bwdkorder",
            name="guest_checkout",
            field=models.BooleanField(
                default=False,
                help_text="سفارش بدون ورود به سایت ساخته شده؛ مالک واقعی بعد از پرداخت از روی شماره موبایل پیدا می‌شود.",
            ),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="stock_reserved",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="reservation_expires_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="verify_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="last_verify_attempt_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="finalized_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="needs_review",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="bwdkorder",
            name="review_note",
            field=models.TextField(blank=True),
        ),
    ]
