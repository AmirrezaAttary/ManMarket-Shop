from django.contrib.sitemaps import Sitemap
from shop.models import ProductModel,ProductStatusType,ProductCategoryModel,Brand
from django.urls import reverse


class ProductModelSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return ProductModel.objects.filter(status=ProductStatusType.publish.value)

    def lastmod(self, obj):
        return obj.updated_date

    def location(self, obj):
        return obj.get_absolute_url()



# class CategorySitemap(Sitemap):
#     changefreq = 'weekly'
#     priority = 0.6

#     def items(self):
#         return ProductCategoryModel.objects.all()

#     def lastmod(self, obj):
#         return obj.updated_date

#     def location(self, obj):
#         return reverse("shop:product-list", kwargs={"category_id": obj.id})



# class BrandSitemap(Sitemap):
#     changefreq = 'monthly'
#     priority = 0.4

#     def items(self):
#         return Brand.objects.all()

#     def lastmod(self, obj):
#         return obj.updated_date

#     def location(self, obj):
#         return reverse("shop:product-list", kwargs={"brand_id": obj.id})