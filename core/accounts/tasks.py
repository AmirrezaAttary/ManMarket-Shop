# accounts/tasks.py
from celery import shared_task
from .models import EmailOTP

@shared_task
def clean_expired_otps():
    EmailOTP.delete_expired()
