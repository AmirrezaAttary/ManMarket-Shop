from django.contrib.sitemaps.views import sitemap
from app.shop.sitemaps import ProductModelSitemap
from app.website.sitemaps import StaticViewSitemap
from app.blog.sitemaps import BlogPostSitemap

sitemaps_dict = {
    'static': StaticViewSitemap,
    'products': ProductModelSitemap,
    'blog': BlogPostSitemap,
}
