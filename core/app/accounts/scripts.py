import requests
from django.conf import settings


def send_bulk_sms(message_text, mobiles, send_date_time=None):
    _X_API_KEY = settings.SMSAPIKEY
    _LINE_NUMBER = settings.SMSLINENUMBER
    """
    ارسال پیامک گروهی با استفاده از API sms.ir

    :param message_text: متن پیامک
    :param mobiles: لیست شماره موبایل‌ها
    :param send_date_time: تاریخ/ساعت ارسال (None برای ارسال فوری)
    :return: دیکشنری پاسخ API
    """
    api_url = "https://api.sms.ir/v1/send/bulk"

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": _X_API_KEY
    }
    
    payload = {
        "lineNumber": _LINE_NUMBER,
        "messageText": message_text,
        "mobiles": mobiles,
    }

    response = requests.post(api_url, headers=headers, json=payload)

    try:
        return response.json()
    except Exception:
        return {"status": 0, "message": "خطا در پردازش پاسخ سرور"}
