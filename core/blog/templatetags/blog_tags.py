from django import template
from blog.models import Post,Category
from django.shortcuts import render,get_object_or_404
from django.utils import timezone

register = template.Library()

@register.inclusion_tag("blog/blog-categories.html")
def postcategory():
    posts = Post.objects.filter(status = 1)
    categoryies = Category.objects.all()
    cat_dict = {}
    for name in categoryies:
        cat_dict[name]=posts.filter(category=name).count()
    return {'categoryies':cat_dict}