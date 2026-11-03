import jdatetime
from django.contrib import admin
from django.utils import timezone

# ستون‌هایی که در لیست ادمین به‌صورت تاریخ شمسی نمایش داده می‌شوند
JALALI_FIELDS = {
    "created_date", "updated_date", "created_at", "updated_at", "timestamp",
    "expiration_date", "last_login", "paid_at", "verified_at", "finalized_at",
    "cancelled_at", "reservation_expires_at", "last_synced_at", "start_date", "end_date",
}


def to_jalali(value, fmt="%Y/%m/%d - %H:%M"):
    if not value:
        return "—"
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return jdatetime.datetime.fromgregorian(datetime=value).strftime(fmt)


class JalaliAdminMixin:
    """ستون‌های تاریخ در لیست ادمین را شمسی (به وقت تهران) نشان می‌دهد؛ مرتب‌سازی هم کار می‌کند."""

    def get_list_display(self, request):
        columns = []
        for name in super().get_list_display(request):
            if isinstance(name, str) and name in JALALI_FIELDS:
                try:
                    model_field = self.model._meta.get_field(name)
                except Exception:
                    columns.append(name)
                    continue
                columns.append(self._jalali_column(name, model_field.verbose_name))
            else:
                columns.append(name)
        return columns

    @staticmethod
    def _jalali_column(field_name, label):
        def column(obj):
            return to_jalali(getattr(obj, field_name, None))

        column.short_description = label
        column.admin_order_field = field_name
        column.__name__ = f"{field_name}_jalali"
        return column
