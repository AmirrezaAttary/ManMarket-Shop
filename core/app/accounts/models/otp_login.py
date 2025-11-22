# accounts/models.py
from django.db import models
import random
from django.utils import timezone
from datetime import timedelta

class OTP_LOGIN(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    code = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() - self.created_at < timedelta(minutes=5)

    @classmethod
    def create_otp(cls, user):
        code = str(random.randint(10000, 99999))
        return cls.objects.create(user=user, code=code)
