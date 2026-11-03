from django.db import models
from django.db.models import JSONField
from ..wallets.models import Wallet
from ..order.models import OrderModel


class PayemntType(models.IntegerChoices):
    cart = 1,'پرداخت با درگاه پرداخت '
    wallet = 2, "پرداخت با کیف پول"
    cart_home = 3, "پرداخت در محل"
    wallet_cart = 4, "ترکیبی کیف پول و درگاه"
    gsm_cart = 5, "پرداخت اقساطی با جی اس ام"
    person = 6 , "پرداخت حضوری"
    refah = 7,"پرداخت با درگاه بانک رفاه"

class PayemntStatusType(models.IntegerChoices):
    pending = 1, "در انتظار"
    success = 2, "پرداخت موفق"
    failed = 3, "پرداخت ناموفق"
    partial = 4, "پرداخت جزئی"  # 👈 اضافه کن


# Create your models here.
class PaymentModel(models.Model):
    authority_id = models.CharField(max_length=255, verbose_name="شناسه پرداخت (Authority)")
    ref_id = models.BigIntegerField(null=True,blank=True, verbose_name="شماره پیگیری (RefID)")
    amount = models.DecimalField(default=0,max_digits=10,decimal_places=0, verbose_name="مبلغ")
    response_json = JSONField(default=dict, verbose_name="پاسخ درگاه")
    response_code = models.IntegerField(null=True,blank=True, verbose_name="کد پاسخ")
    status = models.IntegerField(choices=PayemntStatusType.choices,default=PayemntStatusType.pending.value, verbose_name="وضعیت پرداخت")
    
    payemnt_type = models.IntegerField(choices=PayemntType.choices,default=PayemntType.cart.value, verbose_name="روش پرداخت")
    
    remainder = models.DecimalField(default=0,max_digits=10,decimal_places=0, verbose_name="مبلغ باقیمانده")
    
    wallet = models.ForeignKey(Wallet, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="کیف پول")
    order = models.ForeignKey(OrderModel, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="سفارش")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    def __str__(self):
        return f"Payment - {self.get_status_display()}"

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

    