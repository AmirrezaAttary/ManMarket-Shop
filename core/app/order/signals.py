from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderModel, OrderStatusType
# from .tasks import send_feedback_sms


@receiver(post_save, sender=OrderModel)
def schedule_feedback_sms(sender, instance, created, **kwargs):
    # فقط وقتی تغییر وضعیت به deliverd اتفاق افتاد
    if not created and instance.status == OrderStatusType.deliverd:
        # 🚀 زمان‌بندی بعد از 5 روز
        # send_feedback_sms.apply_async(args=[instance.id], countdown=5*24*60*60)
        pass
