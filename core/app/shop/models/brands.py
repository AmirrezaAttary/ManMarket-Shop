from django.db import models


class Brand(models.Model):
    title = models.CharField(max_length=100, verbose_name="نام برند")
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name="نامک (slug)")
    image = models.ImageField(blank=True,null=True,upload_to="brand/img/", verbose_name="لوگوی برند")

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ["-created_date"]

    def __str__(self):
        return self.title