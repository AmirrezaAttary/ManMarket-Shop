# orders/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import OrderModel, OrderStatusType

@shared_task
def cancel_expired_orders():
    expiration_time = timezone.now() - timedelta(minutes=30)
    expired_orders = OrderModel.objects.filter(
        status=OrderStatusType.pending.value,
        created_date__lt=expiration_time
    )
    for order in expired_orders:
        order.status = OrderStatusType.failed.value
        order.save()
