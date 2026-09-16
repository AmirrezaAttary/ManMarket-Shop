from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.order.models import OrderModel, OrderStatusType
from app.dashboard.api.v1.user.serializers import UserOrderSerializer
from app.dashboard.api.v1.user.permissions import IsCustomer
from app.dashboard.api.v1.user.paginations import LargeResultsSetPagination
from app.payment.models import PaymentModel, PayemntStatusType, PayemntType
from app.payment.zarinpal_client import ZarinPalSandbox
from app.shop.models import ProductColorInventory


PAYMENT_EXPIRATION_MINUTES = 30
SHIPPING_FEE = 150000


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = UserOrderSerializer
    permission_classes = [IsCustomer]
    pagination_class = LargeResultsSetPagination
    http_method_names = ['get', 'head', 'options', 'post']

    def get_queryset(self):
        user = self.request.user
        qs = OrderModel.objects.filter(user=user).order_by('-created_date')
        if self.action == 'retrieve':
            qs = qs.prefetch_related(
                'order_items__product',
                'order_items__color',
            ).select_related('payment', 'coupon')
        return qs

    @action(detail=True, methods=['post'], url_path='retry-payment')
    def retry_payment(self, request, pk=None):
        """
        ساخت لینک پرداخت مجدد برای سفارش‌های «در انتظار پرداخت».

        قوانین:
        - فقط صاحب سفارش می‌تواند پرداخت را مجدداً انجام دهد.
        - سفارش حداکثر ۳۰ دقیقه بعد از ایجاد قابل پرداخت مجدد است.
        - تمام کالاهای سفارش باید در موجودی کافی باشند.
        - پرداخت قبلی باطل می‌شود تا یک سفارش چند پرداخت معتبر همزمان نداشته باشد.
        """
        with transaction.atomic():
            order = (
                OrderModel.objects
                .select_for_update()
                .prefetch_related('order_items__product', 'order_items__color')
                .select_related('payment')
                .filter(user=request.user)
                .filter(pk=pk)
                .first()
            )

            if not order:
                return Response(
                    {"error": "سفارش پیدا نشد."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if order.status != OrderStatusType.pending.value:
                return Response(
                    {
                        "error": "این سفارش در انتظار پرداخت نیست.",
                        "status": order.get_status(),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            expires_at = order.created_date + timedelta(
                minutes=PAYMENT_EXPIRATION_MINUTES
            )

            if timezone.now() >= expires_at:
                order.status = OrderStatusType.failed.value
                order.save(update_fields=["status", "updated_date"])
                return Response(
                    {"error": "مهلت پرداخت این سفارش ۳۰ دقیقه به پایان رسیده و سفارش لغو شده است."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # بررسی موجودی همه آیتم‌ها قبل از ساخت لینک پرداخت
            unavailable_items = []
            for item in order.order_items.all():
                inventory = ProductColorInventory.objects.filter(
                    product_id=item.product_id,
                    color_id=item.color_id,
                ).first()

                if not inventory or inventory.stock < item.quantity:
                    unavailable_items.append({
                        "product_id": item.product_id,
                        "product": item.product.title,
                        "color_id": item.color_id,
                        "quantity": item.quantity,
                        "available_stock": inventory.stock if inventory else 0,
                    })

            if unavailable_items:
                return Response(
                    {
                        "error": "بعضی از کالاهای سفارش دیگر موجودی کافی ندارند.",
                        "unavailable_items": unavailable_items,
                        "can_retry_payment": False,
                    },
                    status=status.HTTP_409_CONFLICT
                )

            # اگر پرداخت قبلی هنوز pending است، آن را باطل کن.
            if order.payment and order.payment.status == PayemntStatusType.pending.value:
                order.payment.status = PayemntStatusType.failed.value
                order.payment.save(update_fields=["status", "updated_date"])

            zarinpal = ZarinPalSandbox()
            amount = int(order.total_price) + SHIPPING_FEE

            callback_url = request.build_absolute_uri(
                reverse("payment:api-v1-payment:verify")
            )
            response = zarinpal.payment_request(callback_url, amount)

            if not isinstance(response, dict):
                return Response(
                    {"error": "خطا در دریافت لینک پرداخت از درگاه."},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            authority = response.get("data", {}).get("authority")
            if not authority:
                return Response(
                    {
                        "error": "درگاه پرداخت نتوانست درخواست پرداخت را ایجاد کند.",
                        "gateway_response": response,
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )

            payment = PaymentModel.objects.create(
                authority_id=authority,
                amount=amount,
                order=order,
                payemnt_type=PayemntType.cart.value,
                status=PayemntStatusType.pending.value,
                response_json=response,
            )

            order.payment = payment
            order.save(update_fields=["payment", "updated_date"])

            payment_url = zarinpal.generate_payment_url(authority)

            return Response(
                {
                    "message": "لینک پرداخت مجدد با موفقیت ایجاد شد.",
                    "payment_url": payment_url,
                    "order_id": order.id,
                    "expires_at": expires_at,
                    "remaining_seconds": max(
                        0, int((expires_at - timezone.now()).total_seconds())
                    ),
                },
                status=status.HTTP_200_OK
            )
