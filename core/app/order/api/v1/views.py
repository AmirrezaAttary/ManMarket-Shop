from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ...models import UserAddressModel, OrderModel, OrderItemModel, OrderStatusType, CouponModel
from ....cart.models import CartModel
from ....payment.saman_client import SamanGateway, toman_to_rial
from ....payment.models import PaymentModel, PayemntType, PayemntStatusType
from .serializers import OrderCheckOutSerializer


class CouponPreviewAPIView(GenericAPIView):
    """مبلغ تخفیف کد را روی سبد فعلی کاربر حساب می‌کند (بدون ساخت سفارش).

    همان منطق checkout (get_discount_for) را صدا می‌زند تا فرانت هیچ‌وقت خودش
    از روی درصد حساب نکند؛ کد «مبلغ ثابت» و «درصدی با سقف» هم درست نمایش داده شوند.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        code = (request.data.get("coupon") or "").strip()
        if not code:
            return Response({"coupon": ["کد تخفیف را وارد کنید."]}, status=status.HTTP_400_BAD_REQUEST)

        coupon = CouponModel.objects.filter(code__iexact=code).first()
        if coupon is None:
            return Response({"coupon": ["کد تخفیف وارد شده معتبر نیست."]}, status=status.HTTP_400_BAD_REQUEST)

        cart = CartModel.objects.filter(user=request.user).first()
        subtotal = int(cart.calculate_total_price()) if cart else 0
        try:
            discount = coupon.get_discount_for(request.user, subtotal)
        except DjangoValidationError as e:
            return Response({"coupon": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "coupon": coupon.code,
            "summary": coupon.get_summary(),
            "subtotal": subtotal,
            "discount": int(discount),
            "total": subtotal - int(discount),
        })


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

        # ایجاد سفارش و اعمال کد تخفیف در یک تراکنش:
        # اگر کد قابل استفاده نباشد، سفارشی ساخته نمی‌شود و پیام خطا برمی‌گردد.
        try:
            with transaction.atomic():
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

                # اعمال کد تخفیف (قفل ردیف کد تا دو سفارش هم‌زمان ظرفیت را رد نکنند)
                if coupon_code:
                    coupon_obj = (
                        CouponModel.objects.select_for_update()
                        .filter(code__iexact=coupon_code.strip())
                        .first()
                    )
                    if coupon_obj is None:
                        raise DjangoValidationError("کد تخفیف وارد شده معتبر نیست.")
                    discount = coupon_obj.get_discount_for(user, total_price)
                    total_price = total_price - discount
                    order.coupon = coupon_obj

                total_price = int(total_price)
                order.total_price = total_price
                order.save()
        except DjangoValidationError as e:
            return Response({"coupon": e.messages}, status=status.HTTP_400_BAD_REQUEST)

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