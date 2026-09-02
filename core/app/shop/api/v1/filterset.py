import django_filters

from ...models import ProductModel


class ProductFilter(django_filters.FilterSet):

    category = django_filters.CharFilter(
        method="filter_category",
        label="Category"
    )

    brand = django_filters.CharFilter(
        method="filter_brand",
        label="Brand"
    )

    color = django_filters.CharFilter(
        method="filter_color",
        label="Color"
    )

    min_price = django_filters.NumberFilter(
        method="filter_min_price",
        label="Minimum price"
    )

    max_price = django_filters.NumberFilter(
        method="filter_max_price",
        label="Maximum price"
    )

    in_stock = django_filters.BooleanFilter(
        method="filter_in_stock",
        label="In stock"
    )

    has_discount = django_filters.BooleanFilter(
        method="filter_has_discount",
        label="Has discount"
    )

    spec = django_filters.CharFilter(
        method="filter_spec",
        label="Specifications"
    )

    class Meta:
        model = ProductModel
        fields = []

    def filter_category(self, queryset, name, value):
        if not value:
            return queryset

        slugs = [
            s.strip()
            for s in value.split(",")
            if s.strip()
        ]

        return queryset.filter(
            category__slug__in=slugs
        )

    def filter_brand(self, queryset, name, value):
        if not value:
            return queryset

        slugs = [
            s.strip()
            for s in value.split(",")
            if s.strip()
        ]

        return queryset.filter(
            brand__slug__in=slugs
        )

    def filter_color(self, queryset, name, value):
        if not value:
            return queryset

        ids = [
            c.strip()
            for c in value.split(",")
            if c.strip()
        ]

        return queryset.filter(
            color_inventories__color__id__in=ids
        ).distinct()

    def filter_min_price(self, queryset, name, value):
        if value is None:
            return queryset

        return queryset.filter(
            color_inventories__stock__gt=0,
            color_inventories__price__gt=0,
            color_inventories__final_price__gte=value,
        ).distinct()

    def filter_max_price(self, queryset, name, value):
        if value is None:
            return queryset

        return queryset.filter(
            color_inventories__stock__gt=0,
            color_inventories__price__gt=0,
            color_inventories__final_price__lte=value,
        ).distinct()

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(
                color_inventories__stock__gt=0
            ).distinct()

        if value is False:
            return queryset.exclude(
                color_inventories__stock__gt=0
            ).distinct()

        return queryset

    def filter_has_discount(self, queryset, name, value):
        if value is True:
            return queryset.filter(
                color_inventories__stock__gt=0,
                color_inventories__discount_percent__gt=0
            ).distinct()

        if value is False:
            return queryset.exclude(
                color_inventories__stock__gt=0,
                color_inventories__discount_percent__gt=0
            ).distinct()

        return queryset

    def filter_spec(self, queryset, name, value):
        if not value:
            return queryset

        pairs = [
            p.strip()
            for p in value.split(",")
            if ":" in p
        ]

        for pair in pairs:
            spec_name, spec_value = pair.split(":", 1)

            queryset = queryset.filter(
                specifications__name=spec_name.strip(),
                specifications__value=spec_value.strip(),
            )

        return queryset.distinct()