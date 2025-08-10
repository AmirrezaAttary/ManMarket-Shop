from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """ضرب دو عدد"""
    try:
        return int(float(value) * float(arg))
    except (ValueError, TypeError):
        return ''
