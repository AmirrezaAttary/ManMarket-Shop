from rest_framework import serializers
from django.contrib.auth import get_user_model
from ....validators import validate_iranian_cellphone_number
from ....models import OTP

User = get_user_model()


class OTPRequestSerializer(serializers.Serializer):
    """
    درخواست ارسال کد یکبار مصرف برای شماره موبایل
    """
    phone_number = serializers.CharField(max_length=12)

    def validate_phone_number(self, value):
        validate_iranian_cellphone_number(value)
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("کاربری با این شماره وجود ندارد.")
        return value


class OTPVerifySerializer(serializers.Serializer):
    """
    تایید کد یکبار مصرف و ورود با آن
    """
    phone_number = serializers.CharField(max_length=12)
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        code = attrs.get("code")

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            raise serializers.ValidationError(
                {"phone_number": "کاربری با این شماره یافت نشد."}
            )

        otp = (
            OTP.objects.filter(user=user, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if not otp or not otp.is_valid():
            raise serializers.ValidationError(
                {"code": "کد وارد شده نامعتبر است یا منقضی شده."}
            )

        attrs["user"] = user
        attrs["otp"] = otp
        return attrs
