from django.db import models

class MegaMenu(models.Model):
    category = models.ForeignKey("shop.ProductCategoryModel", on_delete=models.CASCADE, related_name="mega_menus", verbose_name="دسته‌بندی")
    brand = models.ForeignKey("shop.Brand", on_delete=models.CASCADE, verbose_name="برند")

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    class Meta:
        verbose_name = "مگا منو"
        verbose_name_plural = "مگا منوها"
        ordering = ['created_date']

    def __str__(self):
        return self.brand.title