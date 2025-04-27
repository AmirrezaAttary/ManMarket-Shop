from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")
    
    
    
class Color(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title



class ProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    category = models.ForeignKey("ProductCategoryModel", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True,unique=True)
    image = models.ImageField(default="/default/product-image.png",upload_to="product/img/")
    description = models.TextField()
    brief_description = models.TextField(null=True,blank=True)
    
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.draft.value)
    
    avg_rate = models.FloatField(default=0.0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return self.title  
    
    def is_published(self):
        return self.status == ProductStatusType.publish.value
    
    
    
    
class ProductCategoryModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True,unique=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return self.title
    
    
class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE,related_name="product_images")
    file = models.ImageField(upload_to="product/extra-img/")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
        
class ProductColorInventory(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="color_inventories")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="product_inventories")
    stock = models.PositiveIntegerField(default=0)
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)

    def get_price(self):
        discount_amount = self.price * (Decimal(self.discount_percent) / Decimal('100'))
        discounted_price = self.price - discount_amount
        return round(discounted_price)

    def is_discounted(self):
        return self.discount_percent != 0

    class Meta:
        unique_together = ("product", "color")  # هر محصول فقط یک بار یک رنگ خاص داشته باشد.

    def __str__(self):
        return f"{self.product.title} - {self.color.title}"

        
class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product.title
    
    

