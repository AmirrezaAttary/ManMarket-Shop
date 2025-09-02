from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from blog.models import Post, Category,BlogStatusType
from blog.api.v1.serializers import (
    PostSerializerList,
    PostSerializerDetail,
    CategorySerializer
    )

from blog.api.v1.paginations import LargeResultsSetPagination

class PostModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(status=BlogStatusType.publish.value)
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["title", "content"]
    ordering_fields = ["published_date"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostSerializerList
        return PostSerializerDetail


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    search_fields = ["name"]
    ordering_fields = ["created_at"]