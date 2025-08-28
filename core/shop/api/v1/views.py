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
    ProductCategorySerializer,
    BrandSerializer,
    ColorSerializer,
    ProductColorInventorySerializer,
    ProductImageModelSerializer,
    ProductSpecificationSerializer,
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