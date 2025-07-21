from django import template
from django.utils import timezone
from website.models import Story,ReviewStatusType

register = template.Library()

@register.inclusion_tag("includes/story_index.html")
def show_story():
    storys = Story.objects.filter(status=ReviewStatusType.accepted.value)
    return {'storys':storys}