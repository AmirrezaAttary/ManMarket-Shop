from django.db import models
from django.utils import timezone


class OTP(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, verbose_name="کاربر")
    code = models.CharField(max_length=6, verbose_name="کد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    is_used = models.BooleanField(default=False, verbose_name="استفاده شده")

    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 300

    @classmethod
    def create_otp(cls, user):
        import secrets

        # همیشه ۶ رقم؛ با صفر ابتدایی هم مشکلی ندارد.
        code = f"{secrets.randbelow(1_000_000):06d}"
        return cls.objects.create(user=user, code=code)

    class Meta:
        verbose_name = "کد یکبارمصرف"
        verbose_name_plural = "کدهای یکبارمصرف"
