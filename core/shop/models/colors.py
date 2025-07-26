from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Min


class Color(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["-id"]
    
class ProductColorInventory(models.Model):
    product = models.ForeignKey("shop.ProductModel", on_delete=models.CASCADE, related_name="color_inventories")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="product_inventories")
    stock = models.PositiveIntegerField(default=0)
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    hex_color = models.CharField(max_length=7, default="#000000")  # Hex color code
    updated_date = models.DateTimeField(auto_now=True)
    
    def get_price(self):
        discount_amount = self.price * (Decimal(self.discount_percent) / Decimal('100'))
        discounted_price = self.price - discount_amount
        return round(discounted_price)
    
    def get_price_product(self):
        return round(self.price)

    def is_discounted(self):
        return self.discount_percent != 0

    class Meta:
        unique_together = ("product", "color")  # هر محصول فقط یک بار یک رنگ خاص داشته باشد.

    def __str__(self):
        return f"{self.product.title} - {self.color.title}"