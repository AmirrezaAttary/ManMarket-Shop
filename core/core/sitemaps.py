
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import ProductModelSitemap
from website.sitemaps import StaticViewSitemap
from blog.sitemaps import BlogPostSitemap

sitemaps_dict = {
    'static': StaticViewSitemap,
    'products': ProductModelSitemap,
    'blog': BlogPostSitemap,
}
