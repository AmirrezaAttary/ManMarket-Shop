from rest_framework import serializers
from shop.models import Brand

class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id",
            "title",
            "slug",
            "image"
        ]