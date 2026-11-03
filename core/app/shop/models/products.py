from django.db import models
from django.urls import reverse

class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")


class ProductModel(models.Model):
    category = models.ForeignKey("ProductCategoryModel", on_delete=models.SET_NULL, null=True, verbose_name="دسته‌بندی")
    brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, null=True, verbose_name="برند")
    title = models.CharField(max_length=255, verbose_name="عنوان محصول")
    meta_title = models.CharField(max_length=255,null=True,blank=True, verbose_name="عنوان سئو")
    brief_title = models.CharField(max_length=255, blank=True, verbose_name="عنوان کوتاه")
    slug = models.SlugField(allow_unicode=True, unique=True, max_length=200, verbose_name="نامک (slug)")
    image = models.ImageField(default="default/product-image.png",upload_to="product/img/", verbose_name="تصویر اصلی")
    description = models.TextField(verbose_name="توضیحات")
    brief_description = models.TextField(null=True,blank=True, verbose_name="توضیحات کوتاه")
    product_view = models.IntegerField(default=0, verbose_name="تعداد بازدید")
    sales_count = models.PositiveIntegerField(default=0, verbose_name="تعداد فروش")
    warranty = models.CharField(max_length=100, null=True, blank=True, verbose_name="گارانتی")
    
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.publish.value, verbose_name="وضعیت نمایش")
    meta_description = models.CharField(max_length=255,null=True,blank=True, verbose_name="توضیحات سئو")
    avg_rate = models.FloatField(default=0.0, verbose_name="میانگین امتیاز")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
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
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
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
        discounted_colors = self.color_inventories.filter(
            discount_percent__gt=0,
            stock__gt=0
        )

        if not discounted_colors.exists():
            return False

        min_discounted_price = min(
            color.get_price() for color in discounted_colors
        )

        min_price = self.get_min_price()

        if min_price is None:
            return False

        return min_discounted_price < min_price

    def get_absolute_api_url(self):
        return reverse("shop:api-v1-shop:product-detail", kwargs={"slug": self.slug})

    def get_similar_products(self):
        return ProductModel.objects.filter(
            status=ProductStatusType.publish.value,
            brand=self.brand,
            color_inventories__price__gt=0,
            color_inventories__stock__gt=0
        ).exclude(id=self.id).distinct().order_by("-created_date")
    

    def get_min_discounted_price_template(self):
        inventory = (
            self.color_inventories
            .filter(price__gt=0, stock__gt=0)
            .order_by("final_price")
            .first()
        )
        return inventory

    @property
    def min_price_template(self):
        inventory = self.get_min_discounted_price_template()
        return inventory.price if inventory else None


    @property
    def min_discount_percent_template(self):
        inventory = self.get_min_discounted_price_template()
        return inventory.discount_percent if inventory else None