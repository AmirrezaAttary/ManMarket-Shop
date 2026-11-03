from django.db import models

class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE,related_name='wishlist_user', verbose_name="کاربر")
    product = models.ForeignKey("shop.ProductModel",on_delete=models.CASCADE, verbose_name="محصول")
    
    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"
