from django import template
from django.utils import timezone
import jdatetime

register = template.Library()


PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر",
    "مرداد", "شهریور", "مهر", "آبان",
    "آذر", "دی", "بهمن", "اسفند"
]


def to_persian_number(value):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return "".join(persian_digits[int(c)] if c.isdigit() else c for c in str(value))


@register.filter
def pretty_persian_datetime(value):
    if not value:
        return ""

    now = timezone.localtime(timezone.now())
    value = timezone.localtime(value)

    j_date = jdatetime.datetime.fromgregorian(datetime=value)
    j_now = jdatetime.datetime.fromgregorian(datetime=now)

    time_str = f"{value.hour:02d}:{value.minute:02d}"
    time_str = to_persian_number(time_str)

    if j_date.date() == j_now.date():
        return f"امروز {to_persian_number(j_date.day)} {PERSIAN_MONTHS[j_date.month - 1]} ماه ساعت {time_str}"

    elif j_date.date() == (j_now - jdatetime.timedelta(days=1)).date():
        return f"دیروز {to_persian_number(j_date.day)} {PERSIAN_MONTHS[j_date.month - 1]} ماه ساعت {time_str}"

    return f"{to_persian_number(j_date.day)} {PERSIAN_MONTHS[j_date.month - 1]} ماه ساعت {time_str}"
