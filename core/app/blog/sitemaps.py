from django.contrib.sitemaps import Sitemap
from .models import Post,BlogStatusType  # اسم دقیق مدل بلاگ شما

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(status=BlogStatusType.publish.value)  # اگر فیلد منتشر دارد

    def lastmod(self, obj):
        return obj.updated_at  # یا created_date بسته به مدل شما
