from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class PriceSpecification(models.Model):
    """
    Model representing a price get digikala.
    """
    product = models.OneToOneField('shop.ProductModel', null=True, blank=True, on_delete=models.CASCADE, related_name='pricespecification', verbose_name="محصول")
    url = models.URLField(max_length=255,null=True,blank=True, verbose_name="لینک محصول در دیجی‌کالا")
    number_comments = models.IntegerField(null=True, blank=True, default=10,validators=[
                               MinValueValidator(1), MaxValueValidator(100)], verbose_name="تعداد نظرات دریافتی")

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    class Meta:
        verbose_name = "منبع دیجی‌کالا برای مشخصات و نظرات"
        verbose_name_plural = "منابع دیجی‌کالا برای مشخصات و نظرات"
        ordering = ["-created_date"]

    