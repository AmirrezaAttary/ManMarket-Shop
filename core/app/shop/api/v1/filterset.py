# filterset.py
import django_filters
from django.db.models import Min, Q

from ...models import ProductModel


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method="filter_category")
    brand = django_filters.CharFilter(method="filter_brand")
    color = django_filters.CharFilter(method="filter_color")
    min_price = django_filters.NumberFilter(method="filter_min_price")
    max_price = django_filters.NumberFilter(method="filter_max_price")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    has_discount = django_filters.BooleanFilter(method="filter_has_discount")
    # مثال: ?spec=رم:8GB,حافظه:128GB
    spec = django_filters.CharFilter(method="filter_spec")

    class Meta:
        model = ProductModel
        fields = []

    def _annotate_price(self, queryset):
        if "min_product_price" not in queryset.query.annotations:
            queryset = queryset.annotate(
                min_product_price=Min(
                    "color_inventories__final_price",
                    filter=Q(
                        color_inventories__stock__gt=0,
                        color_inventories__price__gt=0,
                    ),
                )
            )
        return queryset

    def filter_category(self, queryset, name, value):
        slugs = [s.strip() for s in value.split(",") if s.strip()]
        return queryset.filter(category__slug__in=slugs)

    def filter_brand(self, queryset, name, value):
        slugs = [s.strip() for s in value.split(",") if s.strip()]
        return queryset.filter(brand__slug__in=slugs)

    def filter_color(self, queryset, name, value):
        ids = [c.strip() for c in value.split(",") if c.strip()]
        return queryset.filter(color_inventories__color__id__in=ids).distinct()

    def filter_min_price(self, queryset, name, value):
        queryset = self._annotate_price(queryset)
        return queryset.filter(min_product_price__gte=value)

    def filter_max_price(self, queryset, name, value):
        queryset = self._annotate_price(queryset)
        return queryset.filter(min_product_price__lte=value)

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(color_inventories__stock__gt=0).distinct()
        return queryset

    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(color_inventories__discount_percent__gt=0).distinct()
        return queryset

    def filter_spec(self, queryset, name, value):
        # ?spec=رم:8GB,حافظه:128GB  -> AND بین همه‌ی مشخصات
        pairs = [p.strip() for p in value.split(",") if ":" in p]
        for pair in pairs:
            spec_name, spec_value = pair.split(":", 1)
            queryset = queryset.filter(
                specifications__name=spec_name.strip(),
                specifications__value=spec_value.strip(),
            )
        return queryset.distinct()