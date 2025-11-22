from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import (
    ProductModel,
    ProductStatusType,
    ProductCategoryModel,
    Brand,
    Color,
)
from .serializers import (
    CategorySerializer,
    BrandsSerializer,
    ColorSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    SimilarProductSerializer,
)
from .paginations import LargeResultsSetPagination
from .filterset import ProductFilter

class ProductModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title"]
    filterset_class = ProductFilter
    search_fields = ["title"]
    ordering_fields = ["created_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=["get"])
    def similar(self, request, pk=None):
        product = self.get_object()
        similar_products = product.get_similar_products()
        serializer = SimilarProductSerializer(similar_products, many=True, context={"request": request})
        return Response(serializer.data)

class ProductCategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = ProductCategoryModel.objects.all()


class BrandModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandsSerializer 
    queryset = Brand.objects.all()


class ColorModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ColorSerializer
    queryset = Color.objects.all()

