from rest_framework import serializers
from app.shop.models import (
    ProductModel,
    ProductCategoryModel, 
    Brand, 
    Color, 
    ProductColorInventory, 
    ProductImageModel
    )

class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel
        fields = [
            "file",
            "color",
        ]

class AdminProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"

class ColorInventorySerializer(serializers.ModelSerializer):
    color = AdminProductColorSerializer(read_only=True)  # به جای فقط id، کل اطلاعات رنگ رو میاره

    class Meta:
        model = ProductColorInventory
        fields = [
            "id",
            "color",
            "stock",
            "price",
            "final_price",
            "discount_percent",
            "hex_color",
            "updated_date"
        ]

class ProductSerializer(serializers.ModelSerializer):
    product_images = ImageModelSerializer(many=True, read_only=True)
    color_inventories = ColorInventorySerializer(many=True, read_only=True)
    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "brief_title",
            "slug",
            "image",
            "description",
            "category",
            "brand",
            "warranty",
            "status",
            "meta_description",
            "absolute_url",
            # روابط
            "product_images",
            "color_inventories",
        ]
        read_only_fields = ["user",]

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)
        else:
            rep.pop("product_images", None)
            rep.pop("color_inventories", None)
        return rep
    
    
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"

