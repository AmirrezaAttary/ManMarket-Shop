# accounts/tasks.py
from celery import shared_task
from .models import EmailOTP
from django.utils import timezone
from datetime import timedelta
from accounts.models import User


@shared_task
def clean_expired_otps():
    EmailOTP.delete_expired()


@shared_task
def delete_unverified_users():
    cutoff = timezone.now() - timedelta(minutes=20)
    users = User.objects.filter(
        created_date__lt=cutoff,
        is_verified=False,
        is_phone_verified=False
    )
    count = users.count()
    users.delete()
    return f"{count} unverified users deleted."
