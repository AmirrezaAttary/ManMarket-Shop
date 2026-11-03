from django.contrib.admin.apps import AdminConfig


class PersianAdminConfig(AdminConfig):
    """جایگزین django.contrib.admin: از PersianAdminSite به‌عنوان ادمین پیش‌فرض استفاده می‌کند."""

    default_site = "core.admin_site.PersianAdminSite"
