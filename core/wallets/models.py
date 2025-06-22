# models.py

from django.db import models

class Wallet(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.user.email
class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    TRANSACTION_TYPES = (
        ('charge', 'شارژ'),
        ('withdraw', 'برداشت'),
        ('payment', 'پرداخت'),
        ('refund', 'برگشت وجه'),
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
