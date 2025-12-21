from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class PriceSpecification(models.Model):
    """
    Model representing a price get digikala.
    """
    product = models.OneToOneField('shop.ProductModel', null=True, blank=True, on_delete=models.CASCADE, related_name='pricespecification')
    url = models.URLField(max_length=255,null=True,blank=True)
    number_comments = models.IntegerField(null=True, blank=True, default=10,validators=[
                               MinValueValidator(1), MaxValueValidator(100)])

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]

    