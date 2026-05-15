from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
from app.payment.models import PaymentModel, PayemntStatusType, PayemntType
from app.payment.zarinpal_client import ZarinPalSandbox
from app.order.models import OrderStatusType



class PaymentVerifyAPIView(APIView):
    """
    تایید پرداخت آنلاین زرین‌پال
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority")
        status_param = request.GET.get("Status")  # 'OK' یا 'NOK'

        success_url = "https://manmarket.ir/payment/successfull"
        failed_url = "https://manmarket.ir/payment/failed"

        if not authority_id:
            return redirect(failed_url)

        payment_obj = get_object_or_404(PaymentModel, authority_id=authority_id)

        if payment_obj.payemnt_type not in [
            PayemntType.cart.value,
            PayemntType.cart_home.value,
            PayemntType.wallet_cart.value,
        ]:
            return redirect(failed_url)

        zarin_pal = ZarinPalSandbox()
        response = zarin_pal.payment_verify(int(payment_obj.amount), payment_obj.authority_id)

        response_data = response.get("data")
        response_errors = response.get("errors")

        payment_obj.response_json = response
        payment_obj.save()

        # اگر پاسخ زرین پال خالی یا خطا داشته باشه => failed
        if not response_data or response_errors:
            payment_obj.status = PayemntStatusType.failed.value
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order:
                order.status = OrderStatusType.failed.value
                order.save()

            return redirect(failed_url)

        # بررسی موفقیت
        is_success = (status_param == "OK" and response_data.get("code") == 100)

        if is_success:
            payment_obj.status = PayemntStatusType.success.value
            payment_obj.ref_id = response_data.get("ref_id")
            payment_obj.response_code = response_data.get("code")
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order:
                order.status = OrderStatusType.awaiting.value
                order.save()

                # کاهش موجودی
                for item in order.order_items.all():
                    inventory = item.color_inventory
                    if inventory.stock >= item.quantity:
                        inventory.stock -= item.quantity
                        inventory.save()
                    else:
                        # موجودی کافی نیست => failed
                        order.status = OrderStatusType.failed.value
                        order.save()

                        payment_obj.status = PayemntStatusType.failed.value
                        payment_obj.save()

                        return redirect(failed_url)

            return redirect(success_url)

        # پرداخت ناموفق
        payment_obj.status = PayemntStatusType.failed.value
        payment_obj.save()

        order = getattr(payment_obj, "order", None)
        if order:
            order.status = OrderStatusType.failed.value
            order.save()

        return redirect(failed_url)
