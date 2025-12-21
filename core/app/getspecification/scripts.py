import re
import requests
import jdatetime
import datetime


def getspecificationDigikala(url):
    match = re.search(r"dkp-(\d+)", url)
    if match:
        product_url = match.group(1)
        api_url = f'https://api.digikala.com/v2/product/{product_url}/'
        response = requests.get(api_url)
        response_json = response.json()
        data_specifications = response_json['data']['product']['specifications']

        item_list = {}
        for item in data_specifications:
            all_item = item['attributes']
            for items in all_item:
                values = items.get('values', [])
                if values:
                    # تبدیل لیست به رشته با جداکننده‌ی " / "
                    item_list[items['title']] = " / ".join(values)
        return item_list
   

import re
import requests
import datetime
import jdatetime
import html


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


ZWNJ = "\u200c"  # نیم‌فاصله

REPLACE_PATTERN = re.compile(
    r"(دیجی‌کالا|دیجی کالا|دی جی کالا|digikala)",
    re.IGNORECASE
)


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\\u200c", ZWNJ)

    text = (
        text
        .replace("ي", "ی")
        .replace("ك", "ک")
    )

    text = REPLACE_PATTERN.sub(f"من{ZWNJ}مارکت", text)

    return text


def text_to_html(text: str) -> str:
    if not text:
        return ""

    # escape برای امنیت
    text = html.escape(text)

    # پاراگراف
    text = re.sub(r"\n{2,}", "</p><p>", text)

    # خط جدید
    text = text.replace("\n", "<br>")

    return f"<p>{text}</p>"


def getCommentsDigikala(url, number_comments=10):
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
                "name": normalize_text(comment.get("user_name", "")),
                "description": text_to_html(raw_body),  # 👈 اینجا اعمال شد
                "rate": comment.get("rate", 0),
                "created_at": jalali_str_to_gregorian(
                    comment.get("created_at", "")
                )
            })

        if page >= pager.get("total_pages", 1):
            break

        page += 1

    return results


print(getCommentsDigikala("https://www.digikala.com/product/dkp-16736269/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-s24-fe-%D8%AF%D9%88-%D8%B3%DB%8C%D9%85-%DA%A9%D8%A7%D8%B1%D8%AA-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D9%88-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85/",100))