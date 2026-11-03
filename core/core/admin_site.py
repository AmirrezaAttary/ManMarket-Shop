from django.contrib import admin

from .admin_mixins import JalaliAdminMixin


class PersianAdminSite(admin.AdminSite):
    site_header = "پنل ادمین من مارکت"
    site_title = "ادمین من مارکت"
    index_title = "مدیریت داده‌های فروشگاه"
    site_url = "/dashboard/admin/home/"

    def register(self, model_or_iterable, admin_class=None, **options):
        admin_class = admin_class or admin.ModelAdmin
        if not issubclass(admin_class, JalaliAdminMixin):
            admin_class = type(
                admin_class.__name__, (JalaliAdminMixin, admin_class), {"__module__": admin_class.__module__}
            )
        return super().register(model_or_iterable, admin_class, **options)

    # برچسب فارسی برای اپ‌های شخص‌ثالث که ترجمه‌ی فارسی ندارند
    APP_LABELS = {"django_summernote": "ویرایشگر متن", "taggit": "برچسب‌ها"}
    MODEL_LABELS = {"Attachments": "پیوست‌ها", "Attachment": "پیوست"}

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            app["name"] = self.APP_LABELS.get(app["app_label"], app["name"])
            for model in app["models"]:
                model["name"] = self.MODEL_LABELS.get(model["name"], model["name"])
        return app_list
