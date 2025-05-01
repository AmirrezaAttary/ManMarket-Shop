from django.db.models import OuterRef, Subquery, DecimalField, ExpressionWrapper, F, Min, Max
from django.views.generic import ListView, DetailView
from shop.models import (ProductModel, ProductStatusType,
                         ProductColorInventory,ProductCategoryModel,
                         ProductSpecification,Brand)
# Create your views here.

class ShopListProductView(ListView):
    template_name = 'shop/product_list.html'
    paginate_by = 12
    

    def get_queryset(self):
        queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)

        search_q = self.request.GET.get('q')
        if search_q:
            queryset = queryset.filter(title__icontains=search_q)

        category_ids = self.request.GET.getlist('category_id')
        if category_ids:
            queryset = queryset.filter(category__id__in=category_ids)

        brand_ids = self.request.GET.getlist('brand_id')
        if brand_ids:
            queryset = queryset.filter(brand__id__in=brand_ids)

        min_price = self.request.GET.get('min_price')
        if min_price:
            queryset = queryset.filter(color_inventories__price__gte=min_price)

        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(color_inventories__price__lte=max_price)

        order_by = self.request.GET.get("order_by")
        if order_by:
            if order_by == "visited":
                queryset = queryset.order_by("-product_view")
            elif order_by == "newest":
                queryset = queryset.order_by("-created_date")
            elif order_by == "popular":
                queryset = queryset.order_by("-avg_rate")
            elif order_by == "cheap":
                queryset = queryset.annotate(min_price=Min("color_inventories__price")).order_by("min_price")
            elif order_by == "expensive":
                queryset = queryset.annotate(max_price=Max("color_inventories__price")).order_by("-max_price")
            queryset = queryset.annotate(min_price=Min("color_inventories__price"))
        discounted_price_expr = ExpressionWrapper(
            F('price') - (F('price') * F('discount_percent') / 100),
            output_field=DecimalField()
        )

        # زیرکوئری گرفتن کمترین قیمت تخفیف خورده
        discounted_inventory = ProductColorInventory.objects.filter(
            product=OuterRef('pk')
        ).annotate(
            discounted_price=discounted_price_expr
        ).order_by('discounted_price')

        min_discounted_price_subquery = Subquery(
            discounted_inventory.values('discounted_price')[:1]
        )

        min_discount_percent_subquery = Subquery(
            discounted_inventory.values('discount_percent')[:1]
        )

        queryset = queryset.annotate(
            min_discounted_price=min_discounted_price_subquery,
            min_discount_percent=min_discount_percent_subquery
        )
        return queryset.distinct()
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.get_queryset().count()
        context["categories"] = ProductCategoryModel.objects.all()
        context["brands"] = Brand.objects.all()
        return context
    
    
class ShopDetailProductView(DetailView):
    template_name = 'shop/product_detail.html'
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # هر بار که صفحه دیده می‌شود، 1 واحد به بازدید افزوده می‌شود
        ProductModel.objects.filter(pk=obj.pk).update(product_view=F('product_view') + 1)
        
        return obj
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['product']

        # تمام رنگ‌ها
        colors = ProductColorInventory.objects.filter(product=product)

        # محاسبه قیمت تخفیف‌خورده برای هر رنگ
        for color in colors:
            color.discounted_price = color.price - (color.price * color.discount_percent / 100)

        # پیدا کردن رنگ با کمترین قیمت تخفیف‌خورده
        default_color = min(colors, key=lambda c: c.discounted_price, default=None)

        context['colors'] = colors
        context['default_color'] = default_color
        context['specifications'] = ProductSpecification.objects.filter(product=product)

        return context