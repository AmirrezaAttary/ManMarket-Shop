from django.db.models import Case, When, Value, IntegerField, Min
from django.db.models import Q
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
    MegaMenu
)
from .serializers import (
    CategorySerializer,
    BrandsSerializer,
    ProductColorSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    SimilarProductSerializer,
    MegaMenuSerializer
)
from .paginations import LargeResultsSetPagination
from .filterset import ProductFilter
from urllib.parse import unquote
from rest_framework.generics import get_object_or_404
from rest_framework.generics import ListAPIView




class ProductModelViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title"]
    ordering_fields = ["created_date"]
    lookup_field = "slug"
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        slug = self.kwargs.get(lookup_url_kwarg)

        # اصلاح double-encoding احتمالی
        if isinstance(slug, str):
            slug = unquote(slug)

        obj = get_object_or_404(queryset, **{self.lookup_field: slug})
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        base_qs = ProductModel.objects.filter(
            status=ProductStatusType.publish.value
        )

        if self.action == "list":
            # ترتیب: اول محصولات با stock>0 و price>0، بعد بر اساس جدیدترین
            return (
                base_qs
                .annotate(
                    has_stock_and_price=Case(
                        When(
                            color_inventories__stock__gt=0,
                            color_inventories__price__gt=0,
                            then=Value(1)
                        ),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                )
                .distinct()
                .order_by(
                    "-has_stock_and_price",  # محصولات با موجودی و قیمت اول
                    "-created_date"          # سپس جدیدترین‌ها
                )
            )

        return base_qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=["get"])
    def similar(self, request, slug=None):
        product = self.get_object()
        similar_products = product.get_similar_products()
        serializer = SimilarProductSerializer(similar_products, many=True, context={"request": request})
        return Response(serializer.data)


class ProductCategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = ProductCategoryModel.objects.all()
    lookup_field = "slug"


class BrandModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandsSerializer 
    queryset = Brand.objects.all()
    lookup_field = "slug"


class ColorModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductColorSerializer
    queryset = Color.objects.all()

class MegaMenuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MegaMenu.objects.select_related(
        "category",
        "brand"
    ).all()

    serializer_class = MegaMenuSerializer