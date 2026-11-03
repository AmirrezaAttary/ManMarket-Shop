from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from django_jalali.db import models as jmodels
# Create your models here.

class BlogStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")
    

class Post(models.Model):
    image = models.ImageField(upload_to='blog/images',default='blog/images/default.jpg', verbose_name="تصویر شاخص")
    title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
    content = models.TextField(verbose_name="محتوا")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    category = models.ManyToManyField("Category", verbose_name="دسته‌بندی‌ها")
    status = models.IntegerField(choices=BlogStatusType.choices,default=BlogStatusType.publish.value, verbose_name="وضعیت")
    slug = models.SlugField(allow_unicode=True,unique=True,max_length=200, verbose_name="نامک (slug)")
    tags = TaggableManager(verbose_name="برچسب‌ها")
    meta_description = models.CharField(max_length=255,null=True,blank=True, verbose_name="توضیحات سئو")
    
    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def is_published(self):
        return self.status == BlogStatusType.publish.value
    
    def get_absolute_url(self):
        return reverse('blog:blog-detail', args=[self.slug])
    
    def get_first_category(self):
        return self.category.first()

    def get_absolute_api_url(self):
        return reverse(
            "blog:api-v1-blog:post-detail",
            kwargs={"slug": self.slug}
        )


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(allow_unicode=True, blank=True, null=True, max_length=200, verbose_name="نامک (slug)")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دسته‌بندی بلاگ"
        verbose_name_plural = "دسته‌بندی‌های بلاگ"


class PostProduct(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_products', verbose_name="مقاله")
    product = models.ForeignKey('shop.ProductModel', on_delete=models.CASCADE, related_name='post_products', verbose_name="محصول")
    
    def __str__(self):
        return f"{self.post.title} - {self.product.title}"
    
    class Meta:
        verbose_name = "پست محصول"
        verbose_name_plural = "پست محصولات"