from django.db import models

class MegaMenu(models.Model):
    category = models.ForeignKey("shop.ProductCategoryModel", on_delete=models.CASCADE, related_name="mega_menus")
    brand = models.ForeignKey("shop.Brand", on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return self.brand.title