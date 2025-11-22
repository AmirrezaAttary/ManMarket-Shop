from rest_framework import serializers
from ....models import ProductCategoryModel

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryModel
        fields = [
            "id",
            "title",
            "slug",
            "image"
        ]