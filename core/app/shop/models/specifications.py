from django.db import models

class ProductSpecification(models.Model):
    product = models.ForeignKey("shop.ProductModel", on_delete=models.CASCADE, related_name='specifications', verbose_name="محصول")
    name = models.CharField(max_length=255, verbose_name="عنوان مشخصه")  # مثلا: حافظه داخلی
    value = models.CharField(max_length=1000, verbose_name="مقدار")  # مثلا: 256 گیگابایت
    status = models.BooleanField(default=False, verbose_name="نمایش داده شود")  # فعال یا غیرفعال بودن مشخصه

    def __str__(self):
        return f"{self.name}: {self.value}"

    class Meta:
        verbose_name = "مشخصه محصول"
        verbose_name_plural = "مشخصات محصول"

 