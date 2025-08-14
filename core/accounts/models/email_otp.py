from django.db import models
from django.utils import timezone
from datetime import timedelta

class EmailOTP(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """اعتبارسنجی کد OTP تا ۲ دقیقه"""
        return (
            not self.is_used and 
            timezone.now() - self.created_at < timedelta(minutes=2)
        )

    @classmethod
    def delete_expired(cls):
        """پاک کردن OTP های منقضی شده"""
        expiration_time = timezone.now() - timedelta(minutes=2)
        cls.objects.filter(created_at__lt=expiration_time).delete()

    def __str__(self):
        return f"{self.user} - {self.code}"
