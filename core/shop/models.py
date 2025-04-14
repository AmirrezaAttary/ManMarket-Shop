from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")


class ProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    category = models.ForeignKey("ProductCategoryModel", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True,unique=True)
    image = models.ImageField(default="/default/product-image.png",upload_to="product/img/")
    description = models.TextField()
    brief_description = models.TextField(null=True,blank=True)
    
    
    
    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.draft.value)
    price = models.DecimalField(default=0,max_digits=10,decimal_places=0)
    discount_percent = models.IntegerField(default=0,validators = [MinValueValidator(0),MaxValueValidator(100)])
    
    avg_rate = models.FloatField(default=0.0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return self.title
    
    def get_price(self):        
        discount_amount = self.price * Decimal(self.discount_percent / 100)
        discounted_amount = self.price - discount_amount
        return '{:,}'.format(round(discounted_amount)) 
    
    def is_discounted(self):
        return self.discount_percent != 0
    
    def is_published(self):
        return self.status == ProductStatusType.publish.value
    
    def get_price_by_color(self, color_id):
        """گرفتن قیمت محصول بر اساس رنگ انتخاب شده"""
        variant = self.color_variants.filter(color_id=color_id).first()
        if variant:
            return variant.price
        return self.get_price()
    
    
    
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
        
        
class ProductColor(models.Model):
    title = models.CharField(max_length=100)
    hex_value = models.CharField(max_length=7)  # برای ذخیره مقدار رنگ به صورت HEX (مثلاً #FF5733)

    def __str__(self):
        return self.title

        
class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product.title
    
    
class ProductColorVariant(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="color_variants")
    color = models.ForeignKey("ProductColor", on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)  # قیمت مخصوص این رنگ

    def __str__(self):
        return f"{self.product.title} - {self.color.title} - {self.price} تومان"
    
    
class ProductSpecifications(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="specifications")
    title = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.title} - {self.title} : {self.value}"
