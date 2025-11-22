import requests
import json
from django.conf import settings

class GSMPay:
    _payment_request_url = "https://api.gsmpay.ir/v1/cpg/payments"
    _payment_verify_url = "https://api.gsmpay.ir/v1/cpg/payments/verify"
    _payment_reverse_url = "https://api.gsmpay.ir/v1/cpg/payments/reverse"

    def __init__(self, merchant_code=settings.GSMPAY_MERCHANT_CODE):
        self.merchant_code = merchant_code

    def create_payment(self, callback_url, invoice_reference, invoice_amount, invoice_date,
                       payer_mobile, payer_first_name, payer_last_name, payer_national_code,
                       description=None, items=None):
        """
        ایجاد شناسه پرداخت (توکن)
        """
        total_amount = (invoice_amount) * 10
        payload = {
            "merchant_code": self.merchant_code,
            "callback_url": callback_url,
            "invoice_reference": invoice_reference,
            "invoice_amount": total_amount,
            "invoice_date": invoice_date,
            "payer_mobile": payer_mobile,
            "payer_first_name": payer_first_name,
            "payer_last_name": payer_last_name,
            "payer_national_code": payer_national_code,
            "description": description,
            "items": items or []
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(self._payment_request_url, headers=headers, data=json.dumps(payload))
        return response.json(), response.status_code

    def verify_payment(self, token, invoice_reference, invoice_amount):
        """
        تایید پرداخت پس از بازگشت کاربر از درگاه
        """
        payload = {
            "merchant_code": self.merchant_code,
            "token": token,
            "invoice_reference": invoice_reference,
            "invoice_amount": invoice_amount
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(self._payment_verify_url, headers=headers, data=json.dumps(payload))
        return response.json(), response.status_code

    def reverse_payment(self, token, reverse_amount):
        """
        برگشت مبلغ سفارش
        """
        payload = {
            "merchant_code": self.merchant_code,
            "token": token,
            "reverse_amount": reverse_amount
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(self._payment_reverse_url, headers=headers, data=json.dumps(payload))
        return response.json(), response.status_code
