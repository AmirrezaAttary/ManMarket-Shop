from blog.api.v1.serializers import PostSerializer,CategorySerializer
from blog.models import Post, Category
from rest_framework import viewsets


class PostModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=True)
    search_fields = ["title", "content"]
    ordering_fields = ["created_at"]


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    search_fields = ["name"]
    ordering_fields = ["created_at"]