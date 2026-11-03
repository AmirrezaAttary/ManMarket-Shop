from django.db import models

# Create your models here.
class CartModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE, verbose_name="کاربر")

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    def __str__(self):
        return f"{self.user}"
    
    def calculate_total_price(self):
        return sum(item.color_inventory.get_price() * item.quantity for item in self.cart_items.all())

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"
        
    
class CartItemModel(models.Model):
    cart = models.ForeignKey(CartModel,on_delete=models.CASCADE,related_name="cart_items", verbose_name="سبد خرید") 
    product = models.ForeignKey('shop.ProductModel',on_delete=models.PROTECT, verbose_name="محصول")
    color = models.ForeignKey('shop.Color',on_delete=models.PROTECT, verbose_name="رنگ")
    color_inventory = models.ForeignKey('shop.ProductColorInventory',on_delete=models.PROTECT, verbose_name="قیمت و موجودی رنگ")
    quantity = models.PositiveIntegerField(default=0, verbose_name="تعداد")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    def __str__(self):
        return f"{self.product.title} - {self.cart.id}"

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
