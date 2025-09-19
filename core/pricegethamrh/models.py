from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class PriceGetHamrh(models.Model):
    """
    Model representing a price get hamrh.
    """
    product = models.ForeignKey('shop.ProductModel',null=True,blank=True,on_delete=models.CASCADE)
    url = models.URLField(max_length=255,null=True,blank=True, unique=True)
    url_kasra = models.URLField(max_length=255,null=True,blank=True, unique=True)
    profit = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )


    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]

    