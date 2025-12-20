from rest_framework import serializers
from taggit.serializers import (TagListSerializerField, TaggitSerializer)   
from app.blog.models import Post,Category
from app.shop.models import ProductModel

# class PostSerializer(serializers.Serializer):
#     id =  serializers.IntegerField()
#     title = serializers.CharField(max_length=250)


class PostCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"



class PostSerializerList(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "image",
            "title",
            "slug",
            "category",            
            "relative_url",
            "absolute_url",
            "created_at"
        ]

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"
    

    def get_category(self, obj):
        first_category = obj.get_first_category()
        if first_category:
            return {
                "id": first_category.id,
                "name": first_category.name,
                "slug": first_category.slug
            }
        return None






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






class PostSerializerDetail(serializers.ModelSerializer):
    category = PostCategorySerializer(many=True)
    tags = TagListSerializerField()


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

        ]
