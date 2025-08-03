from django.db import models

class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE,related_name='wishlist_user')
    product = models.ForeignKey("shop.ProductModel",on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product.title