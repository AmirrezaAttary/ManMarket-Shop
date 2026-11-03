import csv
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View

from core.admin_mixins import to_jalali

from ....accounts.models import User, UserType
from ...permissions import HasAdminAccessPermission


class AdminCustomersPhonesExportView(LoginRequiredMixin, HasAdminAccessPermission, View):
    """دانلود CSV شماره موبایل مشتریان فعال (مثلاً برای ارسال به تیم مارکتینگ دیجی‌کالا)."""

    def get(self, request):
        customers = (
            User.objects.filter(type=UserType.customer.value, is_active=True)
            .exclude(phone_number__isnull=True)
            .exclude(phone_number="")
            .select_related("user_profile")
            .order_by("id")
        )
        # BOM در ابتدای فایل تا اکسل فارسی را درست نشان بدهد
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="customers-phones-{date.today():%Y%m%d}.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(["شماره موبایل", "نام", "نام خانوادگی", "تاریخ عضویت"])
        for user in customers:
            profile = getattr(user, "user_profile", None)
            first = (getattr(profile, "first_name", "") or "").strip()
            last = (getattr(profile, "last_name", "") or "").strip()
            writer.writerow([
                user.phone_number,
                "" if first in ("None", "کاربر جدید") else first,
                "" if last == "None" else last,
                to_jalali(user.created_date, "%Y/%m/%d"),
            ])
        return response
