from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class PriceGetHamrh(models.Model):
    """
    Model representing a price get hamrh.
    """
    product = models.ForeignKey('shop.ProductModel',null=True,blank=True,on_delete=models.CASCADE, verbose_name="محصول")
    url = models.URLField(max_length=255,null=True,blank=True, unique=True, verbose_name="لینک قیمت (همراه)")
    url_kasra = models.URLField(max_length=255,null=True,blank=True, unique=True, verbose_name="لینک قیمت (کسری)")
    profit = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="درصد سود"
    )


    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    class Meta:
        verbose_name = "لینک قیمت‌گیری خودکار"
        verbose_name_plural = "لینک‌های قیمت‌گیری خودکار"
        ordering = ["-created_date"]

    