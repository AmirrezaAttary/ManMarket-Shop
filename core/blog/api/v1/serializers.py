from rest_framework import serializers
from blog.models import Post

# class PostSerializer(serializers.Serializer):
#     id =  serializers.IntegerField()
#     title = serializers.CharField(max_length=250)



class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"