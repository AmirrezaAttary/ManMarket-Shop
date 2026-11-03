from django.db import models



class ProductImageModel(models.Model):
    product = models.ForeignKey("shop.ProductModel",on_delete=models.CASCADE,related_name="product_images", verbose_name="محصول")
    color = models.ForeignKey("shop.Color", on_delete=models.CASCADE, related_name="product_images", null=True, blank=True, verbose_name="رنگ")
    file = models.ImageField(upload_to="product/extra-img/", verbose_name="فایل تصویر")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        ordering = ["created_date"]