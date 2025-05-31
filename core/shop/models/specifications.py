from django.db import models

class ProductSpecification(models.Model):
    product = models.ForeignKey("shop.ProductModel", on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=255)  # مثلا: حافظه داخلی
    value = models.CharField(max_length=255)  # مثلا: 256 گیگابایت

    def __str__(self):
        return f"{self.name}: {self.value}"

 