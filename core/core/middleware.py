from django.conf import settings
from django.utils import translation


class AdminPersianMiddleware:
    """
    ادمین جنگو (مسیر /admin/) را فارسی و راست‌چین می‌کند.

    عمداً زبان کل پروژه (LANGUAGE_CODE) را عوض نمی‌کنیم تا پیام‌های API، فرمت اعداد و
    تمپلیت‌های داشبورد همان‌طور که هستند بمانند؛ فقط درخواست‌های ادمین با زبان فارسی اجرا می‌شوند.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.prefix = "/" + getattr(settings, "ADMIN_URL_PREFIX", "admin/").lstrip("/")

    def __call__(self, request):
        if not request.path.startswith(self.prefix):
            return self.get_response(request)
        translation.activate("fa")
        request.LANGUAGE_CODE = "fa"
        try:
            response = self.get_response(request)
        finally:
            translation.deactivate()
        response.headers.setdefault("Content-Language", "fa")
        return response
