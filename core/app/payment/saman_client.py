import requests
from django.conf import settings


def toman_to_rial(amount):
    """سامان مبلغ را به ریال می‌گیرد؛ پروژه‌ی شما با تومان کار می‌کند."""
    return int(amount) * 10


class SamanGateway:
    """
    کلاینت درگاه پرداخت اینترنتی بانک سامان (SEP / OnlinePG).

    - واحد مبلغ در این درگاه «ریال» است.
    - انتقال کاربر به درگاه با فرم POST و فیلد مخفی Token انجام می‌شود.
    - بانک بعد از پرداخت، کاربر را با POST به RedirectUrl برمی‌گرداند
      (پارامترها: State, RefNum, ResNum, RRN, TraceNo, Amount, ...).
    """

    _token_url = "https://sep.shaparak.ir/onlinepg/onlinepg"
    page_url = "https://sep.shaparak.ir/OnlinePG/OnlinePG"
    _verify_url = "https://sep.shaparak.ir/verifyTxnRandomSessionkey/ipg/VerifyTransaction"
    _reverse_url = "https://sep.shaparak.ir/verifyTxnRandomSessionkey/ipg/ReverseTransaction"

    def __init__(self, terminal_id=None):
        self.terminal_id = str(terminal_id or settings.SAMAN_TERMINAL_ID)

    def _post(self, url, payload):
        try:
            response = requests.post(url, json=payload, timeout=15)
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            return {"_transport_error": str(exc)}

    def payment_request(self, callback_url, amount_rial, res_num, mobile_number=None):
        """
        درخواست توکن. پاسخ موفق: {"status": 1, "token": "..."}
        res_num باید برای هر تراکنش یکتا باشد (ما id رکورد PaymentModel را می‌دهیم).
        """
        payload = {
            "action": "token",
            "TerminalId": self.terminal_id,
            "Amount": int(amount_rial),
            "ResNum": str(res_num),
            "RedirectUrl": callback_url,
        }
        if mobile_number:
            payload["CellNumber"] = mobile_number
        return self._post(self._token_url, payload)

    def _ref_payload(self, ref_num):
        terminal = int(self.terminal_id) if self.terminal_id.isdigit() else self.terminal_id
        return {"RefNum": ref_num, "TerminalNumber": terminal}

    def payment_verify(self, ref_num):
        """تأیید تراکنش. موفق: ResultCode == 0 و Success == True"""
        return self._post(self._verify_url, self._ref_payload(ref_num))

    def payment_reverse(self, ref_num):
        """برگشت تراکنش (استرداد وجه به کارت مشتری)."""
        return self._post(self._reverse_url, self._ref_payload(ref_num))