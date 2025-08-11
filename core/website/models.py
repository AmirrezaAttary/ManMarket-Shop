from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255,null=True, blank=True)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']
    def __str__(self):
        return self.name
    
    
class AboutGrop(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='about/',default='about/default.png')
    job = models.CharField(max_length=255)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']
    def __str__(self):
        return self.name
    
    
    
class ReviewStatusType(models.IntegerChoices):
    pending = 1, "در انتظار تایید"
    accepted = 2, "تایید شده"
    rejected = 3, "رد شده"


User = get_user_model()

class Story(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=255, verbose_name='تایتل')
    video = models.FileField(upload_to='stories/videos/', verbose_name='فیلم')
    icon = models.ImageField(upload_to='stories/icons/', verbose_name='آیکون استوری')
    status = models.IntegerField(
            choices=ReviewStatusType.choices, default=ReviewStatusType.pending.value, verbose_name='آیکون استوری')
    product = models.ForeignKey('shop.ProductModel', on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "استوری"
        verbose_name_plural = "استوری‌ها"

    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def get_status(self):
        return {
            "id":self.status,
            "title":ReviewStatusType(self.status).name,
            "label":ReviewStatusType(self.status).label,
        }