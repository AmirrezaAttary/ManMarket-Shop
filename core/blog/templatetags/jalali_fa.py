from django import template
import jdatetime

register = template.Library()

@register.filter
def to_jalali_farsi(value):
    if not value:
        return ''
    try:
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        day = str(jalali_date.day)
        month = months[jalali_date.month - 1]
        year = str(jalali_date.year)
        return f"{day} {month} {year}"
    except Exception as e:
        return str(value)
