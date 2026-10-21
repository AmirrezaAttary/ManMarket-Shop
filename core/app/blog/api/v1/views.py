
from urllib.parse import unquote

from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from app.blog.models import Post, Category, BlogStatusType
from app.blog.api.v1.serializers import (
    PostSerializerList,
    PostSerializerDetail,
    PostCategorySerializer,
)
from app.blog.api.v1.paginations import LargeResultsSetPagination


class PostModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializerDetail
    pagination_class = LargeResultsSetPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ["category"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at"]  # اگر این فیلد در مدل وجود دارد

    lookup_field = "slug"

    def get_queryset(self):
        return Post.objects.filter(
            status=BlogStatusType.publish.value
        )

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = (
            self.lookup_url_kwarg or self.lookup_field
        )

        slug = self.kwargs.get(lookup_url_kwarg)

        # رفع double-encoding احتمالی اسلاگ
        if isinstance(slug, str):
            previous_slug = None

            while slug != previous_slug:
                previous_slug = slug
                decoded_slug = unquote(slug)

                if decoded_slug == slug:
                    break

                slug = decoded_slug

        obj = get_object_or_404(
            queryset,
            **{self.lookup_field: slug},
        )

        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == "list":
            return PostSerializerList

        return PostSerializerDetail


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostCategorySerializer
    queryset = Category.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = ["name"]
    ordering_fields = ["created_at"]
