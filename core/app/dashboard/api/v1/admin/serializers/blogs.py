from rest_framework import serializers
from app.blog.models import Post,Category
from taggit.serializers import (TagListSerializerField, TaggitSerializer)


class PostSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    tags = TagListSerializerField()
    
    class Meta:
        model = Post
        fields = [
            "image",
            "title",
            "content",
            "category",
            "status",
            "slug",
            "tags",
            "meta_description",
            "absolute_url"
        ]
    
    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)

        return rep
        
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"
    
    
class DashboardPostCategorySerializer(serializers.ModelSerializer):
    
    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "absolute_url"
        ]
    
    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)

        return rep
        
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"