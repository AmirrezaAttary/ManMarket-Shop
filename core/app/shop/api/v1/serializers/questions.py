from rest_framework import serializers

from ....models import ProductModel, ProductQuestion


class ProductQuestionSerializer(serializers.ModelSerializer):
    """پرسش‌های تاییدشده‌ی یک محصول؛ کاربر فقط می‌تواند پرسش جدید ثبت کند."""

    product = serializers.SlugRelatedField(slug_field="slug", queryset=ProductModel.objects.all())
    asked_by = serializers.SerializerMethodField()

    class Meta:
        model = ProductQuestion
        fields = ["id", "product", "question", "answer", "asked_by", "created_date"]
        read_only_fields = ["id", "answer", "asked_by", "created_date"]

    def get_asked_by(self, obj):
        # فقط نام کوچک نمایش داده می‌شود (نام کامل کاربر عمومی نشود)
        profile = getattr(obj.user, "user_profile", None) if obj.user_id else None
        first_name = (getattr(profile, "first_name", "") or "").strip()
        if not first_name or first_name in ("None", "کاربر جدید"):
            return "کاربر من مارکت"
        return first_name

    def validate_question(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("پرسش خیلی کوتاه است.")
        return value
