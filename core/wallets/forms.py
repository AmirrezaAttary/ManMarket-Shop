# wallets/forms.py
from django import forms

class WalletChargeForm(forms.Form):
    amount = forms.IntegerField(min_value=1000, label="مبلغ شارژ (تومان)")
