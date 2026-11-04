import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0016_persian_labels'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponmodel',
            name='discount_type',
            field=models.CharField(choices=[('percent', 'درصدی'), ('percent_capped', 'درصدی با سقف'), ('fixed', 'مبلغ ثابت')], default='percent', max_length=20, verbose_name='نوع تخفیف'),
        ),
        migrations.AddField(
            model_name='couponmodel',
            name='max_discount_amount',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='سقف تخفیف (تومان)'),
        ),
        migrations.AddField(
            model_name='couponmodel',
            name='discount_amount',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='مبلغ تخفیف ثابت (تومان)'),
        ),
        migrations.AddField(
            model_name='couponmodel',
            name='min_order_amount',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='حداقل مبلغ سفارش (تومان)'),
        ),
        migrations.AddField(
            model_name='couponmodel',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='فعال'),
        ),
        migrations.AddField(
            model_name='couponmodel',
            name='per_user_limit',
            field=models.PositiveIntegerField(default=1, verbose_name='حداکثر استفاده‌ی هر کاربر (۰ = نامحدود)'),
        ),
        migrations.AlterField(
            model_name='couponmodel',
            name='discount_percent',
            field=models.IntegerField(blank=True, default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='درصد تخفیف'),
        ),
    ]
