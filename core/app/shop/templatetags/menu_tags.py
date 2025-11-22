# shop/templatetags/shop_tags.py
from django import template
from ..models import MegaMenu, ProductCategoryModel

register = template.Library()

@register.simple_tag
def get_mega_menus(category_slug):
    category = ProductCategoryModel.objects.filter(slug=category_slug).first()
    if category:
        return MegaMenu.objects.filter(category=category).select_related('brand')
    return []