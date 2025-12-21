import re
import requests
import datetime
import jdatetime
import html

# نگاشت ماه‌های فارسی به میلادی
PERSIAN_MONTHS = {
    "فروردین": 1,
    "اردیبهشت": 2,
    "خرداد": 3,
    "تیر": 4,
    "مرداد": 5,
    "شهریور": 6,
    "مهر": 7,
    "آبان": 8,
    "آذر": 9,
    "دی": 10,
    "بهمن": 11,
    "اسفند": 12,
}

# تبدیل تاریخ جلالی به میلادی
def jalali_str_to_gregorian(date_str: str):
    """
    '28 آذر 1404' -> datetime.datetime
    """
    if not date_str:
        return None

    match = re.match(r"(\d{1,2})\s+(\S+)\s+(\d{4})", date_str)
    if not match:
        return None

    day = int(match.group(1))
    month_name = match.group(2)
    year = int(match.group(3))

    month = PERSIAN_MONTHS.get(month_name)
    if not month:
        return None

    jalali_date = jdatetime.date(year, month, day)
    gregorian_date = jalali_date.togregorian()

    return datetime.datetime.combine(gregorian_date, datetime.time.min)

# جایگزینی نام برند
REPLACE_PATTERN = re.compile(
    r"(دیجی‌کالا|دیجی کالا|دی جی کالا|digikala)",
    re.IGNORECASE
)

def normalize_text(text: str) -> str:
    """
    نرمال‌سازی متن:
    - تبدیل حروف عربی به فارسی
    - جایگزینی نام برند با فاصله عادی
    """
    if not text:
        return ""

    # تبدیل escape نیم‌فاصله یا کاراکترهای خاص به فاصله عادی
    text = text.replace("\\u200c", " ").replace("\u200c", " ")

    # نرمال‌سازی حروف عربی → فارسی
    text = text.replace("ي", "ی").replace("ك", "ک")

    # جایگزینی نام برند با فاصله
    text = REPLACE_PATTERN.sub("من مارکت", text)

    return text

def text_to_html(text: str) -> str:
    """
    تبدیل متن به HTML امن با حفظ خطوط و پاراگراف‌ها
    """
    if not text:
        return ""

    # escape برای امنیت
    text = html.escape(text)

    # پاراگراف
    text = re.sub(r"\n{2,}", "</p><p>", text)

    # خط جدید
    text = text.replace("\n", "<br>")

    return f"<p>{text}</p>"

def getCommentsDigikala(url, number_comments=15):
    """
    دریافت کامنت‌ها از دیجی‌کالا و تبدیل مناسب متن و تاریخ
    """
    match = re.search(r"dkp-(\d+)", url)
    if not match:
        return []

    product_id = match.group(1)
    base_url = f"https://api.digikala.com/v1/rate-review/products/{product_id}/"

    results = []
    page = 1

    while len(results) < number_comments:
        try:
            response = requests.get(base_url, params={"page": page}, timeout=10)
            response.raise_for_status()
            data = response.json().get("data", {})
        except Exception:
            break

        comments = data.get("comments", [])
        pager = data.get("pager", {})

        if not comments:
            break

        for comment in comments:
            if len(results) >= number_comments:
                break

            raw_body = normalize_text(comment.get("body", ""))

            results.append({
                "name": normalize_text(comment.get("user_name", "")),  # فاصله عادی
                "description": text_to_html(raw_body),                # HTML امن
                "rate": comment.get("rate", 0),
                "created_at": jalali_str_to_gregorian(comment.get("created_at", ""))
            })

        if page >= pager.get("total_pages", 1):
            break

        page += 1

    return results




