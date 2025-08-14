import requests

def send_bulk_sms(api_key, line_number, message_text, mobiles, send_date_time=None):
    """
    ارسال پیامک گروهی با استفاده از API sms.ir

    :param api_key: کلید API دریافتی از sms.ir
    :param line_number: شماره خط اختصاصی
    :param message_text: متن پیامک
    :param mobiles: لیست شماره موبایل‌ها
    :param send_date_time: تاریخ/ساعت ارسال (None برای ارسال فوری)
    :return: دیکشنری پاسخ API
    """
    api_url = "https://api.sms.ir/v1/send/bulk"

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }

    payload = {
        "lineNumber": line_number,
        "messageText": message_text,
        "mobiles": mobiles,
        "sendDateTime": send_date_time
    }

    response = requests.post(api_url, headers=headers, json=payload)

    try:
        return response.json()
    except Exception:
        return {"status": 0, "message": "خطا در پردازش پاسخ سرور"}



result = send_bulk_sms(
    api_key="co6QLJNKUrO0x75n94cWToUcFxsD4TEQGaiNXqlhR9THVrh6B5bBdXDayfe0asCb",
    line_number="30004007672729",
    message_text="سلام خوش آمدی",
    mobiles=["09159526624", "09330570810"]
)

if result.get("status") == 1:
    # موفق
    pass
else:
    # ناموفق
    pass
