from rest_framework import viewsets
from shop.models import (
    ProductModel,
    ProductStatusType,
    ProductCategoryModel,
    Brand,
    Color,
    ProductColorInventory,
    ProductImageModel,
    ProductSpecification
)
from shop.api.v1.serializers import (
    CategorySerializer,
    BrandsSerializer,
    ColorSerializer,
    ProductListSerializer,
    ProductDetailSerializer
)


class ProductModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer


class ProductCategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = ProductCategoryModel.objects.all()


class BrandModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandsSerializer 
    queryset = Brand.objects.all()


class ColorModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ColorSerializer
    queryset = Color.objects.all()

