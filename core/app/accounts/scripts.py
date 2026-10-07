import requests
from django.conf import settings


def send_bulk_sms(message_text, mobiles, send_date_time=None):
    """ارسال پیامک گروهی با API نسخه 1 سرویس sms.ir."""
    api_key = settings.SMSAPIKEY
    line_number = settings.SMSLINENUMBER
    api_url = "https://api.sms.ir/v1/send/bulk"

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }

    payload = {
        "lineNumber": line_number,
        "messageText": message_text,
        "mobiles": mobiles,
    }

    if send_date_time is not None:
        payload["sendDateTime"] = send_date_time

    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=20,
    )
    response.raise_for_status()

    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError("پاسخ نامعتبر از سرویس پیامک دریافت شد.") from exc

    # sms.ir در پاسخ‌های خطا معمولاً status صفر برمی‌گرداند.
    # در صورت وجود status، موفقیت را صریح بررسی می‌کنیم.
    api_status = result.get("status") if isinstance(result, dict) else None
    if api_status is not None and str(api_status).lower() not in {"1", "true", "200", "success"}:
        message = result.get("message") or "سرویس پیامک ارسال را تایید نکرد."
        raise RuntimeError(str(message))

    return result
