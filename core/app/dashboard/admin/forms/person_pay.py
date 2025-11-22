# dashboard/forms.py

from django import forms
from ....payment.models import PaymentModel, PayemntType, PayemntStatusType
from ....order.models import OrderModel


class InPersonPaymentForm(forms.ModelForm):
    order = forms.ModelChoiceField(
        queryset=OrderModel.objects.filter(payment__isnull=True),
        label="سفارش",
        help_text="سفارش‌هایی که هنوز پرداخت ندارند"
    )

    class Meta:
        model = PaymentModel
        fields = ['order', 'amount']
        labels = {
            'amount': 'مبلغ پرداخت‌شده',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.payemnt_type = PayemntType.person
        instance.status = PayemntStatusType.success
        instance.authority_id = "in_person"
        instance.ref_id = 0
        instance.response_json = {"info": "پرداخت حضوری توسط ادمین ثبت شد."}
        if commit:
            instance.save()
            # اتصال سفارش به پرداخت
            order = self.cleaned_data['order']
            order.payment = instance
            order.status = 2  # در حال پردازش
            order.save()
        return instance
