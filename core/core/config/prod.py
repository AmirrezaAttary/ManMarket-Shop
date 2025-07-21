from core.settings import *
from decouple import config

SECRET_KEY = 'django-insecure-jc35qo)gv(idt+zlq=2&!yq%y)twxum-$8@s^#3dj^7n^!yn_e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = [
    '192.168.73.237',
    '127.0.0.1',
    'manmarket.ir',
    'www.manmarket.ir',
    'mail.manmarket.ir',  # ← این خط را اضافه کن
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    "https://manmarket.ir",
    "https://www.manmarket.ir",
    "https://mail.manmarket.ir",# اگر از www هم استفاده می‌کنی
]
"""https://api.digikala.com/v1/rate-review/products/18132558/"""