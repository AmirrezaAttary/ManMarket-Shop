from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class AdminChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = self.context['request'].user

        # بررسی رمز فعلی
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "رمز فعلی اشتباه است."})

        # بررسی تطابق رمز جدید و تکرار آن
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "رمز جدید با تکرار آن مطابقت ندارد."})

        # اعتبارسنجی رمز جدید طبق تنظیمات Django
        try:
            validate_password(data['new_password'], user)
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e)})

        return data
