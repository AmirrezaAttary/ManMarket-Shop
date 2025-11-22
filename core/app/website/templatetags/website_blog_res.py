from django import template
from django.utils import timezone
from ...blog.models import Post


register = template.Library()


@register.inclusion_tag("includes/resent.html")
def latestpost(arg=4):
    posts = Post.objects.filter(created_at__lte =timezone.now(),status = 1).order_by('-created_at')[:arg]
    return {'posts': posts}