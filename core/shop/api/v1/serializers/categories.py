from rest_framework import serializers
from shop.models import ProductCategoryModel

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryModel
        fields = [
            "id",
            "title",
            "slug",
            "image"
        ]