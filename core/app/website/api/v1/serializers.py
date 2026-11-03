from rest_framework import serializers

from ...models import (
    Banner,
    FAQ,
    FAQCategory,
    SiteSetting,
)


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        exclude = ["id", "updated_date"]


class BannerSerializer(serializers.ModelSerializer):
    position_display = serializers.CharField(source="get_position_display", read_only=True)

    class Meta:
        model = Banner
        fields = [
            "id", "title", "image", "mobile_image", "link", "alt_text",
            "position", "position_display", "sort_order",
        ]


class FAQSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    category_key = serializers.SerializerMethodField()

    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "category", "category_key", "category_display", "sort_order"]

    def get_category_key(self, obj):
        # مثلاً "order-process" (همان شناسه‌ی تب‌های صفحه‌ی فرانت)
        return FAQCategory(obj.category).name.replace("_", "-")
