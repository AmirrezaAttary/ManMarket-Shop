from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Color(models.Model):
    title = models.CharField(max_length=100, unique=True)
    hex_color = models.CharField(max_length=20, default="#000000")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-id"]


class ProductColorInventory(models.Model):
    product = models.ForeignKey(
        "shop.ProductModel",
        on_delete=models.CASCADE,
        related_name="color_inventories"
    )
    color = models.ForeignKey(
        "shop.Color",
        on_delete=models.CASCADE,
        related_name="product_inventories"
    )
    stock = models.PositiveIntegerField(default=0)

    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    hex_color = models.CharField(max_length=20, default="#000000")
    updated_date = models.DateTimeField(auto_now=True)

    final_price = models.DecimalField(default=0, max_digits=10, decimal_places=0)

    def get_price(self):
        if self.final_price and self.final_price > 0:
            return int(self.final_price)
        return int(self.price)

    def get_price_product(self):
        return int(self.price)

    def is_discounted(self):
        return self.discount_percent > 0

    class Meta:
        unique_together = ("product", "color")

    def __str__(self):
        return f"{self.product.title} - {self.color.title}"


@receiver(pre_save, sender=ProductColorInventory)
def update_prices(sender, instance, **kwargs):
    """
    قبل از ذخیره:
    - اگر final_price داده شده باشه → discount_percent رو حساب کن.
    - اگر فقط discount_percent داده شده باشه → final_price رو حساب کن.
    """
    price = Decimal(instance.price or 0)
    final_price = Decimal(instance.final_price or 0)

    if price > 0 and final_price > 0:
        # ✅ محاسبه درصد تخفیف
        discount = ((price - final_price) / price) * 100
        discount = int(round(discount))

        # اگر تخفیف کمتر از 1٪ بود → بشه 1
        if discount < 1 and price != final_price:
            discount = 1

        instance.discount_percent = discount

    elif price > 0 and instance.discount_percent > 0:
        # ✅ محاسبه قیمت نهایی
        discount_amount = (price * Decimal(instance.discount_percent)) / Decimal(100)
        final_price = price - discount_amount
        instance.final_price = int(round(final_price))
    else:
        # اگر نه تخفیفی بود و نه final_price → قیمت نهایی همون price باشه
        instance.final_price = price
        instance.discount_percent = 0
