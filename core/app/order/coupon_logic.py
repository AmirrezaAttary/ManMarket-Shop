"""محاسبه‌ی مبلغ تخفیف کد تخفیف (بدون وابستگی به جنگو تا ساده تست شود).

همه‌ی مبلغ‌ها به تومان و عدد صحیح هستند.
"""

PERCENT = "percent"
PERCENT_CAPPED = "percent_capped"
FIXED = "fixed"


def compute_discount(discount_type, subtotal, percent=0, max_discount=None, fixed=0):
    """مبلغ تخفیف را برمی‌گرداند؛ هیچ‌وقت بیشتر از جمع سفارش یا منفی نمی‌شود."""
    subtotal = int(subtotal or 0)
    if subtotal <= 0:
        return 0

    if discount_type == FIXED:
        discount = int(fixed or 0)
    else:
        discount = subtotal * int(percent or 0) // 100  # رُند به پایین
        if discount_type == PERCENT_CAPPED and max_discount:
            discount = min(discount, int(max_discount))

    return max(0, min(discount, subtotal))
