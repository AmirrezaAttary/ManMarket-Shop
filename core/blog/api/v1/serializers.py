from rest_framework import serializers
from blog.models import Post,Category

# class PostSerializer(serializers.Serializer):
#     id =  serializers.IntegerField()
#     title = serializers.CharField(max_length=250)



class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"