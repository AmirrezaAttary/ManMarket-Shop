from django.db import models

class ProductCategoryModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(allow_unicode=True,unique=True, verbose_name="نامک (slug)")
    image = models.ImageField(blank=True,null=True,upload_to="category/img/", verbose_name="تصویر دسته‌بندی")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    class Meta:
        verbose_name = "دسته‌بندی محصول"
        verbose_name_plural = "دسته‌بندی‌های محصول"
        ordering = ["created_date"]
        
    def __str__(self):
        return self.title
    