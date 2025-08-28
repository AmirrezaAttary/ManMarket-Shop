from rest_framework import serializers
from taggit.serializers import (TagListSerializerField, TaggitSerializer)   
from blog.models import Post,Category,PostProduct
from shop.models import ProductModel

# class PostSerializer(serializers.Serializer):
#     id =  serializers.IntegerField()
#     title = serializers.CharField(max_length=250)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"



class PostSerializerList(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "image",
            "title",
            "slug",
            "category",
            "created_at"
        ]

    def get_category(self, obj):
        first_category = obj.get_first_category()
        if first_category:
            return {
                "id": first_category.id,
                "name": first_category.name,
                "slug": first_category.slug
            }
        return None


class PostProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostProduct
        fields = "__all__"



class ProductSerializer(serializers.ModelSerializer):
    min_price = serializers.ReadOnlyField(source="get_min_price")
    class Meta:
        model = ProductModel
        fields = [
            "id",
            "title",
            "image",
            "slug",
            "min_price"
        ]  # فیلدهایی که می‌خوای



class PostProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = PostProduct
        fields = ["product"]


class PostSerializerDetail(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    tags = TagListSerializerField()
    post_products = PostProductSerializer(many=True, read_only=True)  # 👈 تغییر دادیم

    class Meta:
        model = Post
        fields = [
            "id",
            "image",
            "title",
            "meta_description",
            "content",
            "category",
            "tags",
            "created_at",
            "post_products"  # 👈 اینجا هم
        ]
