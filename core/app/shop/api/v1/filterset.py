import django_filters
from ...models import ProductModel

class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="exact")
    brand = django_filters.CharFilter(field_name="brand__slug", lookup_expr="exact")

    class Meta:
        model = ProductModel
        fields = ["category", "brand"]
