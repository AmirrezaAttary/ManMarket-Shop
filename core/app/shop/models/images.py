from django.db import models



class ProductImageModel(models.Model):
    product = models.ForeignKey("shop.ProductModel",on_delete=models.CASCADE,related_name="product_images")
    color = models.ForeignKey("shop.Color", on_delete=models.CASCADE, related_name="product_images", null=True, blank=True)
    file = models.ImageField(upload_to="product/extra-img/")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["created_date"]