from django.db import models
from django.urls import reverse

class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")


class ProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    category = models.ForeignKey("ProductCategoryModel", on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True, max_length=200)
    image = models.ImageField(default="default/product-image.png",upload_to="product/img/")
    description = models.TextField()
    brief_description = models.TextField(null=True,blank=True)
    product_view = models.IntegerField(default=0)
    
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.draft.value)
    
    avg_rate = models.FloatField(default=0.0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def get_min_price(self):
        prices = self.color_inventories.filter(price__gt=0).order_by('price').values_list('price', flat=True)
        return prices[0] if prices else None
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return self.title  
    
    def is_published(self):
        return self.status == ProductStatusType.publish.value
    
    def get_absolute_url(self):
        return reverse("shop:product-detail", kwargs={"slug": self.slug})
