from rest_framework import serializers
from shop.models import (
    ProductModel,   
    ProductCategoryModel,
    Brand,
    Color,
    ProductColorInventory,
    ProductImageModel,
    ProductSpecification
)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryModel
        fields = [
            "id",
            "title",
            "slug"
        ]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id",
            "title",
            "slug",
        ]



class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class ProductColorInventorySerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)  # به جای فقط id، کل اطلاعات رنگ رو میاره

    class Meta:
        model = ProductColorInventory
        fields = [
            "id",
            "color",
            "stock",
            "price",
            "discount_percent",
            "hex_color",
        ]



class ProductImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel
        fields = [
            "file",
            "color",
        ]


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = [
            "name",
            "value"
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)  # نمایش کل اطلاعات کتگوری
    min_price = serializers.ReadOnlyField(source="get_min_price")
    min_discounted_price = serializers.ReadOnlyField(source="get_min_discounted_price")
    has_discount = serializers.ReadOnlyField()

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "avg_rate",
            "category",
            "min_price",
            "min_discounted_price",
            "has_discount",
        ]



class ProductDetailSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    product_images = ProductImageModelSerializer(many=True, read_only=True)
    color_inventories = ProductColorInventorySerializer(many=True, read_only=True)

    min_price = serializers.ReadOnlyField(source="get_min_price")
    min_discounted_price = serializers.ReadOnlyField(source="get_min_discounted_price")
    has_discount = serializers.ReadOnlyField()

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "brief_title",
            "slug",
            "image",
            "description",
            "brief_description",
            "product_view",
            "sales_count",
            "warranty",
            "status",
            "meta_description",
            "avg_rate",
            "created_date",
            "updated_date",
            # روابط
            "category",
            "brand",
            "specifications",
            "product_images",
            "color_inventories",
            # خروجی متدهای مدل
            "min_price",
            "min_discounted_price",
            "has_discount",
        ]
