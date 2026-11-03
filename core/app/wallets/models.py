# models.py

from django.db import models

class Wallet(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE,related_name='wallet_user', verbose_name="کاربر")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="موجودی")

    def __str__(self):
        return str(self.user.email) if getattr(self.user, "email", None) else f"Wallet #{self.pk}"

    class Meta:
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف پول‌ها"

    
class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions', verbose_name="کیف پول")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان تراکنش")
    description = models.CharField(max_length=255, verbose_name="توضیحات")
    TRANSACTION_TYPES = (
        ('charge', 'شارژ'),
        ('withdraw', 'برداشت'),
        ('payment', 'پرداخت'),
        ('refund', 'برگشت وجه'),
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="نوع تراکنش")

    class Meta:
        verbose_name = "تراکنش کیف پول"
        verbose_name_plural = "تراکنش‌های کیف پول"
