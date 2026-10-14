from django.core.management.base import BaseCommand

from app.bwdk.services import BWDKService


class Command(BaseCommand):
    help = (
        "Retries Verify (20 min after a failed attempt) and releases expired BWDK reservations. "
        "Run it from cron every 5 minutes when Celery is not running."
    )

    def handle(self, *args, **options):
        done = BWDKService().sync_open_orders()
        self.stdout.write(self.style.SUCCESS(f"bwdk_sync: {done} order(s) checked"))
