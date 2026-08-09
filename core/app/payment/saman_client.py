import requests
from django.conf import settings


class SamanGateway:
    """
    کلاینت درگاه پرداخت اینترنتی بانک سامان (SEP).

    نکات مهم:
    - واحد پول این درگاه ریال است (نه تومان). اگر مبالغ پروژه‌ی شما بر حسب تومان
      محاسبه می‌شود، قبل از ارسال به payment_request باید در ۱۰ ضرب شود.
    - بر خلاف زرین‌پال، انتقال کاربر به درگاه با یک GET ساده انجام نمی‌شود؛
      باید یک فرم HTML با متد POST و یک اینپوت مخفی به نام Token به آدرس
      درگاه ارسال شود (متد build_redirect_form این کار را برایتان انجام می‌دهد).
    """

    _payment_request_url = "https://sep.shaparak.ir/onlinepg/onlinepg"
    _payment_page_url = "https://sep.shaparak.ir/OnlinePG/OnlinePG"
    _payment_verify_url = "https://sep.shaparak.ir/verifyTxnRandomSessionkey/ipg/VerifyTransaction"

    def __init__(self, terminal_id=None):
        self.terminal_id = terminal_id or settings.SAMAN_TERMINAL_ID

    def payment_request(self, callback_url, amount, res_num, mobile_number=None):
        """
        درخواست توکن پرداخت.

        callback_url : آدرسی که سامان بعد از پرداخت کاربر را به آن برمی‌گرداند
        amount       : مبلغ به ریال (عدد صحیح)
        res_num      : شماره یکتای سفارش شما (باید برای هر تراکنش منحصربه‌فرد باشد،
                       معمولاً id سفارش یا id رکورد PaymentModel)
        mobile_number: شماره موبایل خریدار (اختیاری)
        """
        payload = {
            "action": "token",
            "TerminalId": self.terminal_id,
            "Amount": int(amount),
            "ResNum": str(res_num),
            "RedirectUrl": callback_url,
        }
        if mobile_number:
            payload["CellNumber"] = mobile_number

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self._payment_request_url, headers=headers, json=payload, timeout=15
        )
        return response.json()
        # پاسخ موفق چیزی شبیه این است:
        # {"status": 1, "token": "xxxxxxxxxxxxxxxxxxxxx"}
        # پاسخ ناموفق:
        # {"status": 0, "errorCode": "...", "errorDesc": "..."}

    def payment_verify(self, ref_num, cell_number=None, national_code=None):
        """
        تایید نهایی تراکنش بعد از بازگشت کاربر از درگاه.

        ref_num: مقداری است که سامان در callback شما تحت پارامتر RefNum ارسال می‌کند
                 (نه Token و نه ResNum خودتان).
        """
        payload = {
            "RefNum": ref_num,
            "TerminalNumber": self.terminal_id,
            "CellNumber": cell_number or "",
            "NationalCode": national_code or "",
            "IgnoreNationalcode": True,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self._payment_verify_url, headers=headers, json=payload, timeout=15
        )
        return response.json()
        # پاسخ موفق چیزی شبیه این است:
        # {"ResultCode": 0, "ResultDescription": "Success", "Success": true}
        # ResultCode == 0 یعنی تراکنش با موفقیت تایید شده است.

    def build_redirect_form(self, token):
        """
        چون سامان (بر خلاف زرین‌پال) نیاز به POST دارد، این متد یک context
        برمی‌گرداند که می‌توانید مستقیم در یک تمپلیت auto-submit استفاده کنید.
        """
        return {
            "url": self._payment_page_url,
            "token": token,
        }
