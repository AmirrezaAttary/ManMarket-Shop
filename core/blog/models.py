from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from django_jalali.db import models as jmodels
# Create your models here.

class BlogStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")
    

class Post(models.Model):
    image = models.ImageField(upload_to='blog/images',default='blog/images/default.jpg')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField("Category")
    status = models.IntegerField(choices=BlogStatusType.choices,default=BlogStatusType.publish.value)
    slug = models.SlugField(allow_unicode=True,unique=True,max_length=200)
    tags = TaggableManager()
    meta_description = models.CharField(max_length=255,null=True,blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def is_published(self):
        return self.status == BlogStatusType.publish.value
    
    def get_absolute_url(self):
        return reverse('blog:blog-detail', args=[self.slug])


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, blank=True, null=True, max_length=200)
    
    def __str__(self):
        return self.name


class PostProduct(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_products')
    product = models.ForeignKey('shop.ProductModel', on_delete=models.CASCADE, related_name='post_products')
    
    def __str__(self):
        return f"{self.post.title} - {self.product.title}"
    
    class Meta:
        verbose_name = "پست محصول"
        verbose_name_plural = "پست محصولات"