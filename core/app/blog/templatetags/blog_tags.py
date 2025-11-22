from django import template
from ..models import Post,Category

register = template.Library()

@register.inclusion_tag("includes/blog-categories.html")
def postcategory():
    posts = Post.objects.filter(status = 1)
    categoryies = Category.objects.all()
    cat_dict = {}
    for name in categoryies:
        cat_dict[name]=posts.filter(category=name).count()
    return {'categoryies':cat_dict}


@register.inclusion_tag('includes/related_posts.html')
def related_posts():
    posts = Post.objects.filter(status=1).order_by('-created_at')[:4]
    return {'posts': posts}