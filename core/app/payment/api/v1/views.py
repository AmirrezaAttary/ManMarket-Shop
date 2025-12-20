from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from app.payment.models import PaymentModel, PayemntStatusType, PayemntType
from app.payment.zarinpal_client import ZarinPalSandbox
from app.order.models import OrderModel, OrderStatusType
from app.shop.models import ProductColorInventory


class PaymentVerifyAPIView(APIView):
    """
    تایید پرداخت آنلاین زرین‌پال
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority")
        status_param = request.GET.get("Status")  # 'OK' یا 'NOK'

        if not authority_id:
            return Response(
                {"status": "NOK", "message": "پارامتر Authority ارسال نشده است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # پیدا کردن پرداخت
        payment_obj = get_object_or_404(PaymentModel, authority_id=authority_id)

        # فقط پرداخت‌های آنلاین
        if payment_obj.payemnt_type not in [
            PayemntType.cart.value,
            PayemntType.cart_home.value,
            PayemntType.wallet_cart.value,
        ]:
            return Response(
                {"status": "NOK", "message": "روش پرداخت نامعتبر است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # درخواست به زرین پال برای بررسی پرداخت
        zarin_pal = ZarinPalSandbox()
        response = zarin_pal.payment_verify(int(payment_obj.amount), payment_obj.authority_id)

        response_data = response.get("data")
        response_errors = response.get("errors")

        # همیشه پاسخ را ذخیره کن
        payment_obj.response_json = response
        payment_obj.save()

        # اگر پاسخ زرین پال خالی یا دارای خطا بود
        if not response_data or response_errors:
            payment_obj.status = PayemntStatusType.failed.value
            payment_obj.save()

            order = getattr(payment_obj, "order", None)
            if order:
                order.status = OrderStatusType.failed.value  # پرداخت ناموفق
                order.save()

            return Response(
                {
                    "status": "NOK",
                    "message": "پرداخت انجام نشد یا توسط کاربر لغو شد.",
                    "zarinpal_error": response_errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # بررسی موفقیت پرداخت از سمت زرین پال
        is_success = (status_param == "OK" and response_data.get("code") == 100)

        if is_success:
            # ✅ بروزرسانی وضعیت پرداخت
            payment_obj.status = PayemntStatusType.success.value
            payment_obj.ref_id = response_data.get("ref_id")
            payment_obj.response_code = response_data.get("code")
            payment_obj.save()

            # ✅ بروزرسانی سفارش
            order = getattr(payment_obj, "order", None)
            if order:
                order.status = OrderStatusType.awaiting.value  # در حال پردازش
                order.save()

                # کاهش موجودی کالاها
                for item in order.order_items.all():
                    inventory = item.color_inventory
                    if inventory.stock >= item.quantity:
                        inventory.stock -= item.quantity
                        inventory.save()
                    else:
                        # در صورت نبود موجودی کافی
                        order.status = OrderStatusType.failed.value
                        order.save()
                        payment_obj.status = PayemntStatusType.failed.value
                        payment_obj.save()
                        return Response(
                            {
                                "status": "NOK",
                                "message": f"موجودی محصول '{item.product.title}' کافی نیست.",
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

            return Response(
                {
                    "status": "OK",
                    "message": "پرداخت با موفقیت انجام شد.",
                    "ref_id": payment_obj.ref_id,
                    "amount": payment_obj.amount,
                },
                status=status.HTTP_200_OK
            )

        # ❌ در غیر این صورت، پرداخت ناموفق بوده است
        payment_obj.status = PayemntStatusType.failed.value
        payment_obj.save()

        order = getattr(payment_obj, "order", None)
        if order:
            order.status = OrderStatusType.failed.value
            order.save()

        return Response(
            {
                "status": "NOK",
                "message": "پرداخت ناموفق بود.",
                "code": response_data.get("code") if response_data else None,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
