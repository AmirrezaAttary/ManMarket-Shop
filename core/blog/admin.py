from django.contrib import admin
from blog.models import Post,Category

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title','slug','status','created_at')
    prepopulated_fields = {'slug':('title',)}
    
admin.site.register(Category)