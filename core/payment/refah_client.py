import requests
import json
from django.conf import settings


class RefahClient:
    _payment_request_url = "https://pna.shaparak.ir/refipg/api/purchase"
    _payment_verify_url = "https://pna.shaparak.ir/refipg/api/confirm-transaction"
    _payment_page_url = "https://pna.shaparak.ir/refui"

    def __init__(self):
        self.user_name = settings.REFAH_USERNAME
        self.password = settings.REFAH_PASSWORD
        self.terminal_number = settings.REFAH_TERMINAL

    def purchase_request(self, amount, callback_url, order_id, cell_no=None, additional_data=None):
        """
        ارسال درخواست خرید (purchase)
        """
        payload = {
            "userName": self.user_name,
            "password": self.password,
            "amount": float(amount) * 10,
            "callBack": callback_url,
            # "cellNo": cell_no or "",
            # "additionalData": additional_data or "",
            "terminalNumber": int(self.terminal_number),
            "orderId": str(order_id)
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self._payment_request_url,
            headers=headers,
            data=json.dumps(payload)
        )

        try:
            data = response.json()
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid JSON response", "raw": response.text}

        return data 

    def verify_transaction(self, amount, token):
        """
        تأیید تراکنش پس از بازگشت از درگاه (confirm-transaction)
        """
        payload = {
            "userName": self.user_name,
            "password": self.password,
            "amount": float(amount),
            "token": token
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self._payment_verify_url,
            headers=headers,
            data=json.dumps(payload)
        )


        data = response.json()
        print(data)
        return data

    def generate_payment_url(self, token):
        """
        ساخت لینک هدایت کاربر به صفحه پرداخت
        """
        return f"{self._payment_page_url}?token={token}"
