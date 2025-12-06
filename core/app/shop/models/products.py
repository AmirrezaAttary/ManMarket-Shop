from django.db import models
from django.urls import reverse

class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")


class ProductModel(models.Model):
    category = models.ForeignKey("ProductCategoryModel", on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    meta_title = models.CharField(max_length=255,null=True,blank=True)
    brief_title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(allow_unicode=True, unique=True, max_length=200)
    image = models.ImageField(default="default/product-image.png",upload_to="product/img/")
    description = models.TextField()
    brief_description = models.TextField(null=True,blank=True)
    product_view = models.IntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    warranty = models.CharField(max_length=100, null=True, blank=True)
    
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.publish.value)
    meta_description = models.CharField(max_length=255,null=True,blank=True)
    avg_rate = models.FloatField(default=0.0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def get_min_price(self):
        prices = self.color_inventories.filter(price__gt=0, stock__gt=0).order_by('price').values_list('price', flat=True)
        return prices[0] if prices else None
    
    def get_min_discounted_price(self):
        # لیست قیمت‌های تخفیف‌خورده برای رنگ‌های دارای موجودی
        discounted_prices = [
            color.get_price()  # get_price خودش تخفیف را محاسبه می‌کند
            for color in self.color_inventories.filter(price__gt=0, stock__gt=0)
        ]
        return min(discounted_prices) if discounted_prices else None
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return self.title  
    
    def save(self, *args, **kwargs):
        if not self.brief_title:  # Only set brief_title if it's not provided
            self.brief_title = self.title
        super().save(*args, **kwargs)
    
    def is_published(self):
        return self.status == ProductStatusType.publish.value
    
    def get_absolute_url(self):
        return reverse("shop:product-detail", kwargs={"slug": self.slug})

    def has_discount(self):
        discounted_colors = self.color_inventories.filter(discount_percent__gt=0, stock__gt=0)
        if not discounted_colors.exists():
            return False
        # پیدا کردن حداقل قیمت تخفیف خورده از بین این رنگ‌ها
        min_discounted_price = min([color.get_price() for color in discounted_colors])
        
        # پایین‌ترین قیمت محصول (بدون تخفیف)
        min_price = self.get_min_price()
        
        # اگر قیمت تخفیف‌خورده از حداقل قیمت محصول کمتر باشد، تخفیف واقعی داریم
        return min_discounted_price < min_price

    def get_absolute_api_url(self):
        return reverse("shop:api-v1-shop:product-detail", kwargs={"pk": self.pk})

    def get_similar_products(self):
        return ProductModel.objects.filter(
            status=ProductStatusType.publish.value,
            brand=self.brand,
            color_inventories__price__gt=0,
            color_inventories__stock__gt=0
        ).exclude(id=self.id).distinct().order_by("-created_date")