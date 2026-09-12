from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ....models import OTP
from ....scripts import send_bulk_sms
from ..serializers import OTPRequestSerializer, OTPVerifySerializer

User = get_user_model()

# حداقل فاصله‌ی زمانی بین دو درخواست ارسال کد (ثانیه)
OTP_RESEND_COOLDOWN_SECONDS = 60


class OTPRequestAPIView(generics.GenericAPIView):
    """
    درخواست ارسال کد ورود (OTP) به شماره موبایل.
    اگر کد فعالی وجود داشته باشد و هنوز به پایان cooldown نرسیده باشد،
    خطای 429 برمی‌گردد تا از اسپم پیامک جلوگیری شود.
    """
    serializer_class = OTPRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        user = User.objects.get(phone_number=phone_number)

        last_otp = OTP.objects.filter(user=user).order_by("-created_at").first()
        if last_otp:
            seconds_passed = (timezone.now() - last_otp.created_at).seconds
            if seconds_passed < OTP_RESEND_COOLDOWN_SECONDS:
                wait = OTP_RESEND_COOLDOWN_SECONDS - seconds_passed
                return Response(
                    {"detail": f"لطفا {wait} ثانیه دیگر دوباره تلاش کنید."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        otp = OTP.create_otp(user)
        send_bulk_sms(f"کد ورود شما: {otp.code}", [phone_number])

        return Response(
            {"detail": "کد تایید ارسال شد.", "phone_number": phone_number},
            status=status.HTTP_200_OK,
        )


class OTPVerifyAPIView(generics.GenericAPIView):
    """
    تایید کد ارسال‌شده و ورود کاربر.
    در صورت موفقیت، توکن‌های JWT (access/refresh) بازگردانده می‌شود
    تا کاربر بتواند با آن‌ها به عنوان لاگین‌شده به سایر اندپوینت‌ها دسترسی داشته باشد.
    """
    serializer_class = OTPVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp = serializer.validated_data["otp"]

        otp.is_used = True
        otp.save(update_fields=["is_used"])

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
