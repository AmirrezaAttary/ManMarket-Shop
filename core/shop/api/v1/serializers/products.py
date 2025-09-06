from rest_framework import serializers
from rest_framework.reverse import reverse
from shop.models import (
    ProductModel,   
    ProductCategoryModel,
    Brand,
    Color,
    ProductColorInventory,
    ProductImageModel,
    ProductSpecification,
)
from review.models import ReviewModel,ReviewStatusType

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
            "updated_date"
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
            "value",
            "status"
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)  # نمایش کل اطلاعات کتگوری
    min_price = serializers.ReadOnlyField(source="get_min_price")
    min_discounted_price = serializers.ReadOnlyField(source="get_min_discounted_price")
    has_discount = serializers.ReadOnlyField()
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "avg_rate",
            "category",
            "relative_url",
            "absolute_url",
            "min_price",
            "min_discounted_price",
            "has_discount",
        ]

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"


class ReviewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewModel
        fields = [
            "id",
            "user",
            "product",
            "rate",
            "description",
            "created_date",
            "updated_date",
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
    similar_url = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField() 


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
            "reviews",
            # خروجی متدهای مدل
            "similar_url",
            "min_price",
            "min_discounted_price",
            "has_discount",
        ]


    def get_similar_url(self, obj):
        request = self.context.get("request")
        return reverse(
            "shop:api-v1-shop:product-similar",   # اسم روت action مشابه‌ها
            kwargs={"pk": obj.pk},
            request=request,
        )


    def get_reviews(self, obj):
        # فقط reviewهای تایید شده
        accepted_reviews = obj.reviews.filter(status=ReviewStatusType.accepted)
        return ReviewModelSerializer(accepted_reviews, many=True).data



class SimilarProductSerializer(serializers.ModelSerializer):
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField()
    min_price = serializers.ReadOnlyField(source="get_min_price")
    min_discounted_price = serializers.ReadOnlyField(source="get_min_discounted_price")
    get_absolute_url = serializers.URLField(source="get_absolute_url", read_only=True)

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "avg_rate",
            "relative_url",
            "absolute_url",
            "min_price",
            "min_discounted_price",
            "get_absolute_url",
        ]
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        # اسم روت viewset مربوط به محصول رو استفاده کن
        return reverse(
            "shop:api-v1-shop:product-detail",  # اسم route توی router
            kwargs={"pk": obj.pk},
            request=request,
        )