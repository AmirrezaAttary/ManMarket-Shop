# orders/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import OrderModel, OrderStatusType
from ..accounts.scripts import send_bulk_sms

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


@shared_task
def check_order_pending_status(order_id):
    try:
        order = OrderModel.objects.get(id=order_id)
        # بررسی اینکه بعد از 3 دقیقه هنوز pending مونده
        if order.status == OrderStatusType.pending:
            send_bulk_sms(
                message_text=f"مشتری گرامی،\nسفارش شما {order.order_number}\nدر وضعیت «در حال پرداخت» است و تا ۳۰ دقیقه معتبر خواهد بود.\nمـــن مـــارکـــت",
                mobiles=[f"{order.user.phone_number}"]
            )
    except OrderModel.DoesNotExist:
        pass
    
    
@shared_task
def send_feedback_sms(order_id):
    """
    بعد از 5 روز از تحویل سفارش، برای مشتری پیامک نظرخواهی بفرست.
    """
    try:
        order = OrderModel.objects.get(id=order_id)

        # بررسی: آیا سفارش هنوز در حالت deliverd هست؟
        if order.status == OrderStatusType.deliverd:
            send_bulk_sms(
                message_text="مشتری گرامی، نظر شما برای ما ارزشمند است. "
                             "با ثبت دیدگاه خود در من مارکت به بهبود خدمات ما کمک کنید.\n"
                             "ManMarket.ir",
                mobiles=[f"{order.user.phone_number}"]
            )
    except OrderModel.DoesNotExist:
        pass