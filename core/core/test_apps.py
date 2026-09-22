import os
import django
from django.conf import settings
from django.apps import AppConfig

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

for app in settings.INSTALLED_APPS:
    print(f"Checking: {app}")

    try:
        config = AppConfig.create(app)
        print(f"  OK -> {config}")
    except Exception as e:
        print(f"  ERROR -> {type(e).__name__}: {e}")