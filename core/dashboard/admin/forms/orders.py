from django import forms
from order.models import OrderModel

class OrederModelForm(forms.ModelForm):
    remainder = forms.DecimalField(
        label="مانده پرداخت",
        max_digits=10,
        decimal_places=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
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

        # مقدار اولیه remainder را از payment تنظیم کنیم
        if self.instance and self.instance.payment:
            self.fields['remainder'].initial = self.instance.payment.remainder

    def save(self, commit=True):
        order = super().save(commit=False)

        remainder_value = self.cleaned_data.get('remainder')
        if order.payment and remainder_value is not None:
            order.payment.remainder = remainder_value
            order.payment.save()

        if commit:
            order.save()

        return order
