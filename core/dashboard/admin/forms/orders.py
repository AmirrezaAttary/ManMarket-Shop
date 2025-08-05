from django import forms
from order.models import OrderModel
from payment.models import PayemntType

class OrederModelForm(forms.ModelForm):
    remainder = forms.DecimalField(
        label="مانده پرداخت",
        max_digits=10,
        decimal_places=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    authority_id = forms.CharField(
        label="کد پرداخت حضوری (authority_id)",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = OrderModel
        fields = [
            "status",
            "tracking_type",
            "tracking_code",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # افزودن کلاس CSS برای Bootstrap
        self.fields['status'].widget.attrs['class'] = 'form-control'
        self.fields['tracking_type'].widget.attrs['class'] = 'form-control'
        self.fields['tracking_code'].widget.attrs['class'] = 'form-control'

        # مقدار اولیه remainder و authority_id را از payment تنظیم کنیم
        if self.instance and self.instance.payment:
            payment = self.instance.payment
            self.fields['remainder'].initial = payment.remainder

            # فقط اگر پرداخت حضوری بود، authority_id را مقداردهی و فعال کن
            if payment.payemnt_type == PayemntType.person:
                self.fields['authority_id'].initial = payment.authority_id
            else:
                # در غیر این صورت مخفی‌اش کن
                self.fields['authority_id'].widget = forms.HiddenInput()

    def save(self, commit=True):
        order = super().save(commit=False)

        remainder_value = self.cleaned_data.get('remainder')
        authority_id_value = self.cleaned_data.get('authority_id')

        if order.payment:
            if remainder_value is not None:
                order.payment.remainder = remainder_value

            if order.payment.payemnt_type == PayemntType.person and authority_id_value:
                order.payment.authority_id = authority_id_value

            order.payment.save()

        if commit:
            order.save()

        return order
