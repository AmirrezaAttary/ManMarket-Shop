from django.db.models import Case, When, Value, IntegerField, Min, Exists, OuterRef
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
    MegaMenu,
    ProductColorInventory,
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
from django.db.models import Count, Max, Min, Q

from ...models import Brand, Color




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
            #
            # نکته‌ی مهم: قبلاً این annotate با Case/When مستقیم روی
            # color_inventories__stock و color_inventories__price حساب می‌شد
            # که باعث JOIN با جدول ProductColorInventory می‌شد. چون یک محصول
            # می‌تونه چند تا ProductColorInventory داشته باشه، این JOIN باعث
            # می‌شد یک محصول با رنگ‌های مختلف (یکی موجود/باقیمت، یکی نه) چند بار
            # با annotate متفاوت توی queryset تکرار بشه و distinct() هم نمی‌تونست
            # این ردیف‌های تکراری رو یکی کنه (چون مقدار annotate باهاشون فرق داشت).
            # نتیجه: صفحه‌بندی به هم می‌ریخت و محصولات قیمت‌دار/بدون‌قیمت به
            # صورت نامنظم بین صفحات پخش می‌شدن.
            #
            # با Exists(OuterRef(...)) این annotate از طریق یک subquery جدا
            # محاسبه میشه (نه JOIN)، پس هیچ ردیف تکراری‌ای ساخته نمیشه و
            # نیازی هم به distinct() نیست.
            has_available_inventory = ProductColorInventory.objects.filter(
                product=OuterRef("pk"),
                stock__gt=0,
                price__gt=0,
            )

            return (
                base_qs
                .annotate(has_stock_and_price=Exists(has_available_inventory))
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
    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request):
        category_slug = request.query_params.get("category")

        qs = ProductModel.objects.filter(status=ProductStatusType.publish.value)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        price_agg = qs.aggregate(
            min_price=Min(
                "color_inventories__final_price",
                filter=Q(color_inventories__stock__gt=0, color_inventories__price__gt=0),
            ),
            max_price=Max(
                "color_inventories__final_price",
                filter=Q(color_inventories__stock__gt=0, color_inventories__price__gt=0),
            ),
        )

        brands = (
            Brand.objects.filter(productmodel__in=qs)          # ← اسم related رو چک کن
            .annotate(product_count=Count("productmodel", filter=Q(productmodel__in=qs), distinct=True))
            .filter(product_count__gt=0)
            .values("id", "title", "slug", "product_count")
            .distinct()
            .order_by("-product_count")
        )

        colors = (
            Color.objects.filter(product_inventories__product__in=qs)
            .annotate(
                product_count=Count(
                    "product_inventories__product",
                    filter=Q(product_inventories__product__in=qs),
                    distinct=True,
                )
            )
            .filter(product_count__gt=0)
            .values("id", "title", "hex_color", "product_count")
            .distinct()
            .order_by("-product_count")
        )

        return Response({
            "price_range": {
                "min": price_agg["min_price"] or 0,
                "max": price_agg["max_price"] or 0,
            },
            "brands": list(brands),
            "colors": list(colors),
            "in_stock_count": qs.filter(color_inventories__stock__gt=0).distinct().count(),
            "discounted_count": qs.filter(color_inventories__discount_percent__gt=0).distinct().count(),
        })



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