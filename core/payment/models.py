from django.db import models
from django.db.models import JSONField
from wallets.models import Wallet
from order.models import OrderModel


class PayemntType(models.IntegerChoices):
    cart = 1,'پرداخت با کارت بانکی'
    wallet = 2, "پرداخت با کیف پول"
    cart_home = 3, "پرداخت در محل"

class PayemntStatusType(models.IntegerChoices):
    pending = 1, "در انتظار"
    success = 2, "پرداخت موفق"
    failed = 3, "پرداخت ناموفق"
    partial = 4, "پرداخت جزئی"  # 👈 اضافه کن


# Create your models here.
class PaymentModel(models.Model):
    authority_id = models.CharField(max_length=255)
    ref_id = models.BigIntegerField(null=True,blank=True)
    amount = models.DecimalField(default=0,max_digits=10,decimal_places=0)
    response_json = JSONField(default=dict)
    response_code = models.IntegerField(null=True,blank=True)
    status = models.IntegerField(choices=PayemntStatusType.choices,default=PayemntStatusType.pending.value)
    
    payemnt_type = models.IntegerField(choices=PayemntType.choices,default=PayemntType.cart.value)
    
    remainder = models.DecimalField(default=0,max_digits=10,decimal_places=0)
    
    wallet = models.ForeignKey(Wallet, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(OrderModel, null=True, blank=True, on_delete=models.SET_NULL)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment - {self.get_status_display()}"

    