from rest_framework import serializers

from ....models import MegaMenu



class MegaMenuSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    class Meta:
        model = MegaMenu
        fields = [
            "id",
            "category",
            "brand",
            "created_date",
            "updated_date",
        ]

    def get_category(self, obj):
        return {
            "id": obj.category.id,
            "title": obj.category.title,
            "slug": obj.category.slug,
            "image": (
                obj.category.image.url
                if obj.category.image
                else None
            ),
        }

    def get_brand(self, obj):
        return {
            "id": obj.brand.id,
            "title": obj.brand.title,
            "slug": obj.brand.slug,
            "image": (
                obj.brand.image.url
                if obj.brand.image
                else None
            ),
        }