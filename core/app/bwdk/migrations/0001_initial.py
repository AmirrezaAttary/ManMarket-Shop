# Generated manually for ManMarket BWDK integration.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("order", "0015_alter_useraddressmodel_phone_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="BWDKOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("merchant_unique_id", models.CharField(max_length=255, unique=True)),
                ("merchant_order_id", models.CharField(db_index=True, max_length=255)),
                ("order_uuid", models.UUIDField(blank=True, null=True, unique=True)),
                ("order_start_url", models.URLField(blank=True, max_length=1000)),
                ("reference_code", models.CharField(blank=True, max_length=100)),
                ("status", models.IntegerField(choices=[(3, "PENDING"), (4, "WAITING_FOR_GATEWAY"), (5, "EXPIRED"), (7, "PAID_BY_USER"), (8, "FAILED_TO_PAY"), (9, "VERIFIED_BY_MERCHANT"), (17, "REFUND_COMPLETED"), (18, "RESERVATION_EXPIRED"), (19, "DELIVERED"), (20, "SHIPPED")], default=3)),
                ("status_display", models.CharField(blank=True, max_length=100)),
                ("main_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("final_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("total_paid_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("discount_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("promotion_discount_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("tax_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("shipping_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("packing_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("digipay_markup_amount", models.DecimalField(decimal_places=0, default=0, max_digits=14)),
                ("payment_data", models.JSONField(blank=True, default=dict)),
                ("destination_address", models.JSONField(blank=True, default=dict)),
                ("shipping_data", models.JSONField(blank=True, default=dict)),
                ("customer_data", models.JSONField(blank=True, default=dict)),
                ("items_data", models.JSONField(blank=True, default=list)),
                ("last_response", models.JSONField(blank=True, default=dict)),
                ("created_at_bwdk", models.DateTimeField(blank=True, null=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="bwdk_order", to="order.ordermodel")),
            ],
            options={"ordering": ["-created_date"]},
        ),
        migrations.AddIndex(
            model_name="bwdkorder",
            index=models.Index(fields=["status"], name="bwdk_bwdkord_status_8d95a2_idx"),
        ),
    ]
