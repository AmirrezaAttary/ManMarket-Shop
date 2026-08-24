from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ...models import UserAddressModel, OrderModel, OrderItemModel, OrderStatusType, CouponModel
from ....cart.models import CartModel
from ....payment.zarinpal_client import ZarinPalSandbox
from ....payment.models import PaymentModel, PayemntType
from .serializers import OrderCheckOutSerializer


class OrderCheckOutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCheckOutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        address = get_object_or_404(UserAddressModel, id=data['address_id'], user=user)
        tracking_type = data['tracking_type']
        coupon_code = data.get('coupon')

        # گرفتن سبد خرید
        cart = get_object_or_404(CartModel, user=user)
        if cart.cart_items.count() == 0:
            return Response({"error": "سبد خرید شما خالی است."}, status=status.HTTP_400_BAD_REQUEST)

        # ایجاد سفارش
        order = OrderModel.objects.create(
            user=user,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
            tracking_type=tracking_type,
            status=OrderStatusType.awaiting.value
        )

        # ایجاد آیتم‌های سفارش
        for item in cart.cart_items.all():
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                color=item.color_inventory.color,   # ✅ درست
                quantity=item.quantity,
                price=item.color_inventory.get_price()
            )

        # محاسبه کل قیمت
        total_price = order.calculate_total_price()

        # اعمال کوپن
        if coupon_code:
            try:
                coupon_obj = CouponModel.objects.get(code=coupon_code)
                total_price = round(total_price - (total_price * (coupon_obj.discount_percent / 100)))
                order.coupon = coupon_obj
            except CouponModel.DoesNotExist:
                pass  # کوپن اشتباه نادیده گرفته می‌شود

        order.total_price = total_price
        order.save()

        # ایجاد پرداخت زرین‌پال
        zarinpal = ZarinPalSandbox()
        total_price += 150000  # هزینه ارسال ثابت
        callback_url = request.build_absolute_uri(reverse("payment:api-v1-payment:verify"))
        response = zarinpal.payment_request(callback_url, int(total_price))

        payment_obj = PaymentModel.objects.create(
            authority_id=response['data']['authority'],
            amount=total_price,
            order=order,
            payemnt_type=PayemntType.cart.value
        )

        order.payment = payment_obj
        order.save()

        # پاک کردن سبد خرید
        cart.cart_items.all().delete()

        # تولید لینک پرداخت
        payment_url = zarinpal.generate_payment_url(response['data']['authority'])

        return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)
