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
    ProductSerializer,
    ProductCategorySerializer,
    BrandSerializer,
    ColorSerializer,
    ProductColorInventorySerializer,
    ProductImageModelSerializer,
    ProductSpecificationSerializer
)


class ProductModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)


class ProductCategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategoryModel.objects.all()


class BrandModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()


class ColorModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ColorSerializer
    queryset = Color.objects.all()


class ProductColorInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductColorInventorySerializer
    queryset = ProductColorInventory.objects.all()



class ProductImageModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductImageModelSerializer
    queryset = ProductImageModel.objects.all()


class ProductSpecificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSpecificationSerializer
    queryset = ProductSpecification.objects.all()