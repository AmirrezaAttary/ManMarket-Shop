from django import forms
from order.models import UserAddressModel,CouponModel
from django.utils import timezone
from order.models import TrackingType

class CheckOutForm(forms.Form):
    address_id = forms.IntegerField(required=True)
    coupon = forms.CharField(required=False)
    tracking_type = forms.ChoiceField(
        choices=TrackingType.choices,
        required=True,
        label="روش ارسال",
        widget=forms.RadioSelect  # یا Select بسته به نوع نمایش دلخواه
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CheckOutForm, self).__init__(*args, **kwargs)

    def clean_address_id(self):
        address_id = self.cleaned_data.get('address_id')
        user = self.request.user
        try:
            address = UserAddressModel.objects.get(id=address_id, user=user)
        except UserAddressModel.DoesNotExist:
            raise forms.ValidationError("آدرس نامعتبر است.")
        return address

    def clean_coupon(self):
        code = self.cleaned_data.get('coupon')
        if not code:
            return None

        user = self.request.user
        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            raise forms.ValidationError("کد تخفیف اشتباه است")

        if coupon.used_by.count() >= coupon.max_limit_usage:
            raise forms.ValidationError("محدودیت در تعداد استفاده از کد تخفیف")

        if coupon.expiration_date and coupon.expiration_date < timezone.now():
            raise forms.ValidationError("کد تخفیف منقضی شده است")

        if user in coupon.used_by.all():
            raise forms.ValidationError("شما قبلاً از این کد تخفیف استفاده کرده‌اید")

        return coupon