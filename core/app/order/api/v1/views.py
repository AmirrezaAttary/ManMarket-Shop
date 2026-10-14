from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ...models import UserAddressModel, OrderModel, OrderItemModel, OrderStatusType, CouponModel
from ....cart.models import CartModel
from ....payment.saman_client import SamanGateway, toman_to_rial
from ....payment.models import PaymentModel, PayemntType, PayemntStatusType
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
            name=address.name,
            phone_number=address.phone_number,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
            tracking_type=tracking_type,
            status=OrderStatusType.pending.value
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

        # ایجاد پرداخت سامان
        total_price += 150000  # هزینه ارسال ثابت

        # ResNum سامان = id پرداخت، پس اول رکورد را می‌سازیم و بعد توکن می‌گیریم
        payment_obj = PaymentModel.objects.create(
            authority_id="",
            amount=total_price,
            order=order,
            payemnt_type=PayemntType.cart.value
        )

        saman = SamanGateway()
        callback_url = request.build_absolute_uri(reverse("payment:api-v1-payment:verify"))
        payment_link = request.build_absolute_uri(reverse("payment:api-v1-payment:redirect", args=["__T__"]))
        if not settings.DEBUG:
            # پشت reverse proxy ممکن است http ساخته شود؛ سامان و مرورگر https می‌خواهند
            callback_url = callback_url.replace("http://", "https://", 1)
            payment_link = payment_link.replace("http://", "https://", 1)
        response = saman.payment_request(
            callback_url, toman_to_rial(total_price), res_num=payment_obj.id
        )
        token = response.get("token")

        if response.get("status") != 1 or not token:
            payment_obj.status = PayemntStatusType.failed.value
            payment_obj.response_json = response
            payment_obj.save()
            order.status = OrderStatusType.failed.value
            order.save()
            # سبد خرید پاک نمی‌شود تا کاربر بتواند دوباره تلاش کند
            return Response(
                {"error": "ارتباط با درگاه پرداخت برقرار نشد. لطفاً دوباره تلاش کنید."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payment_obj.authority_id = token
        payment_obj.response_json = response
        payment_obj.save()

        order.payment = payment_obj
        order.save()

        # پاک کردن سبد خرید
        cart.cart_items.all().delete()

        # لینک صفحه‌ی واسطی که فرم POST را به سامان ارسال می‌کند
        payment_url = payment_link.replace("__T__", token)

        return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)