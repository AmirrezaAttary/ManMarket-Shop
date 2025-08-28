from blog.api.v1.serializers import PostSerializerList,PostSerializerDetail,CategorySerializer
from blog.models import Post, Category,BlogStatusType
from rest_framework import viewsets


class PostModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(status=BlogStatusType.publish.value)
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostSerializerList
        return PostSerializerDetail


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    search_fields = ["name"]
    ordering_fields = ["created_at"]