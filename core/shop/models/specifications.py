from django.db import models

class ProductSpecification(models.Model):
    product = models.ForeignKey("shop.ProductModel", on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=255)  # مثلا: حافظه داخلی
    value = models.CharField(max_length=600)  # مثلا: 256 گیگابایت
    status = models.BooleanField(default=False)  # فعال یا غیرفعال بودن مشخصه

    def __str__(self):
        return f"{self.name}: {self.value}"

 