from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ....models import OTP
from ....scripts import send_bulk_sms
from ..serializers import OTPRequestSerializer, OTPVerifySerializer

User = get_user_model()

# حداقل فاصله زمانی بین دو درخواست ارسال کد (ثانیه)
OTP_RESEND_COOLDOWN_SECONDS = 60


class OTPRequestAPIView(generics.GenericAPIView):
    """
    درخواست ارسال OTP.

    اگر شماره قبلاً ثبت نشده باشد، یک حساب مشتری برای آن شماره ساخته می‌شود
    و سپس OTP برای همان حساب ارسال می‌گردد.
    """
    serializer_class = OTPRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        # اتمیک بودن فقط برای ساخت کاربر است؛ اگر کاربر از قبل وجود داشته باشد
        # همان کاربر استفاده می‌شود.
        with transaction.atomic():
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    "is_active": True,
                    "is_verified": False,
                },
            )

        last_otp = OTP.objects.filter(user=user).order_by("-created_at").first()
        if last_otp:
            seconds_passed = (timezone.now() - last_otp.created_at).total_seconds()
            if seconds_passed < OTP_RESEND_COOLDOWN_SECONDS:
                wait = max(1, int(OTP_RESEND_COOLDOWN_SECONDS - seconds_passed))
                return Response(
                    {"detail": f"لطفا {wait} ثانیه دیگر دوباره تلاش کنید."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        otp = OTP.create_otp(user)

        try:
            sms_result = send_bulk_sms(
                f"کد ورود شما: {otp.code}\nمن مارکت\nmanmarket.ir",
                [phone_number],
            )
        except Exception as exc:
            # کد ارسال‌نشده نباید قابل استفاده باقی بماند.
            otp.delete()
            return Response(
                {"detail": "مشکل در ارسال کد تایید. لطفا دوباره تلاش کنید."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "detail": "کد تایید ارسال شد.",
                "phone_number": phone_number,
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )


class OTPVerifyAPIView(generics.GenericAPIView):
    """تایید OTP و ورود کاربر با JWT."""
    serializer_class = OTPVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp = serializer.validated_data["otp"]

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        if not user.is_active or not user.is_verified:
            user.is_active = True
            user.is_verified = True
            user.save(update_fields=["is_active", "is_verified"])

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "phone_number": user.phone_number,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )
