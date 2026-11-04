from django import forms
from ....order.models import CouponModel, CouponType


class CouponForm(forms.ModelForm):
    expiration_date = forms.DateTimeField(
        required=False,
        label="تاریخ انقضا",
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
    )

    class Meta:
        model = CouponModel
        fields = [
            "code",
            "discount_type",
            "discount_percent",
            "max_discount_amount",
            "discount_amount",
            "min_order_amount",
            "max_limit_usage",
            "per_user_limit",
            "is_active",
            "expiration_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs.update({'min': 0, 'max': 100})
        self.fields['max_discount_amount'].widget.attrs['min'] = 1
        self.fields['discount_amount'].widget.attrs['min'] = 1
        self.fields['discount_percent'].required = False
        self.fields['discount_amount'].required = False
        self.fields['min_order_amount'].required = False

    def clean_code(self):
        code = (self.cleaned_data.get('code') or '').strip()
        if not code:
            raise forms.ValidationError("کد تخفیف را وارد کنید.")
        duplicates = CouponModel.objects.filter(code__iexact=code)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("این کد تخفیف قبلاً ثبت شده است.")
        return code

    def clean(self):
        cleaned = super().clean()
        dtype = cleaned.get('discount_type')

        # فیلدهای خالی عددی را صفر می‌کنیم
        percent = cleaned.get('discount_percent') or 0
        fixed = cleaned.get('discount_amount') or 0
        cap = cleaned.get('max_discount_amount') or None
        cleaned['min_order_amount'] = cleaned.get('min_order_amount') or 0

        if dtype in (CouponType.percent.value, CouponType.percent_capped.value):
            if not 1 <= percent <= 100:
                self.add_error('discount_percent', "درصد تخفیف باید بین ۱ تا ۱۰۰ باشد.")
            fixed = 0
            if dtype == CouponType.percent_capped.value:
                if not cap:
                    self.add_error('max_discount_amount', "برای این نوع تخفیف، سقف تخفیف را وارد کنید.")
            else:
                cap = None
        elif dtype == CouponType.fixed.value:
            if fixed < 1:
                self.add_error('discount_amount', "مبلغ تخفیف را وارد کنید (حداقل ۱ تومان).")
            percent = 0
            cap = None

        cleaned['discount_percent'] = percent
        cleaned['discount_amount'] = fixed
        cleaned['max_discount_amount'] = cap
        return cleaned
