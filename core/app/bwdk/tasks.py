from celery import shared_task

from .services import BWDKService


@shared_task
def sync_open_bwdk_orders():
    """Celery version of `manage.py bwdk_sync` (run every ~5 minutes)."""
    return BWDKService().sync_open_orders()
