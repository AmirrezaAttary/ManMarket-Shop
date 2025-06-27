from django.db import models


class Brand(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)
    image = models.ImageField(blank=True,null=True,upload_to="brand/img/")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title