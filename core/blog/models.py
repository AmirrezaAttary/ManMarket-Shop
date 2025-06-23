from django.db import models
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
    status = models.IntegerField(choices=BlogStatusType.choices,default=BlogStatusType.draft.value)
    slug = models.SlugField(allow_unicode=True,unique=True)
    tags = TaggableManager()
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def is_published(self):
        return self.status == BlogStatusType.publish.value
    
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name