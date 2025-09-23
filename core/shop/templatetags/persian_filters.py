# shop/templatetags/jalali_tags.py

from django import template
from django.utils.timesince import timesince
from django.utils import timezone

register = template.Library()

PERSIAN_NUMS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
REPLACE_WORDS = {
    "years": "سال",
    "year": "سال",
    "months": "ماه",
    "month": "ماه",
    "weeks": "هفته",
    "week": "هفته",
    "days": "روز",
    "day": "روز",
    "hours": "ساعت",
    "hour": "ساعت",
    "minutes": "دقیقه",
    "minute": "دقیقه",
    "seconds": "ثانیه",
    "second": "ثانیه",
}

@register.filter
def persian_timesince(value):
    if not value:
        return ""
    now = timezone.now()
    delta = timesince(value, now)
    for en, fa in REPLACE_WORDS.items():
        delta = delta.replace(en, fa)
    return delta.translate(PERSIAN_NUMS) + " پیش"
