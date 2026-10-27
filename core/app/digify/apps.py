from django.apps import AppConfig


class DigifyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.digify"
    verbose_name = "Digify catalog feed"

    def ready(self):
        from . import signals  # noqa: F401
