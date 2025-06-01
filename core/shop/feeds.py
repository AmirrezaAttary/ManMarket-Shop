from django.contrib.syndication.views import Feed
from django.urls import reverse
from shop.models import ProductModel,ProductStatusType

class LatestNewsFeed(Feed):
    title = "Latest News from Our shop"
    link = "/rss/feed/"
    description = "Updates on the latest news and announcements."
    
    def items(self):
        return ProductModel.objects.filter(status=ProductStatusType.publish.value)

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.title[:100]