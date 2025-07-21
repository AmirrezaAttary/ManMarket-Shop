from core.settings import *
from decouple import config



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = [
    "https://manmarket.ir",
    "https://www.manmarket.ir",
    "https://mail.manmarket.ir",  # ← این خط را اضافه کن
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    "https://manmarket.ir",
    "https://www.manmarket.ir",
    "https://mail.manmarket.ir",# اگر از www هم استفاده می‌کنی
]
"""https://api.digikala.com/v1/rate-review/products/18132558/"""