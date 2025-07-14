from django.db.models import (OuterRef,
                                Subquery,
                                DecimalField,
                                ExpressionWrapper,
                                F,Min,Max,
                                Prefetch ,Case,
                                When, Value,
                                IntegerField
                                )
from django.views.generic import ListView, DetailView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from shop.models import (ProductModel, ProductStatusType,
                         ProductColorInventory,ProductCategoryModel,
                         ProductSpecification,Brand,WishlistProductModel)
from review.models import ReviewModel,ReviewStatusType
from cart.models import CartItemModel
# Create your views here.


class ShopListProductView(ListView):
    template_name = 'shop/product_list.html'
    paginate_by = 12

    def get_queryset(self):
        queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)

        search_q = self.request.GET.get('q')
        if search_q:
            queryset = queryset.filter(title__icontains=search_q)

        category_ids = self.request.GET.getlist('category')
        if category_ids:
            queryset = queryset.filter(category__slug__in=category_ids)

        brand_ids = self.request.GET.getlist('brand')
        if brand_ids:
            queryset = queryset.filter(brand__slug__in=brand_ids)

        min_price = self.request.GET.get('min_price')
        if min_price:
            queryset = queryset.filter(color_inventories__price__gte=min_price)

        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(color_inventories__price__lte=max_price)

        # annotate برای حداقل و حداکثر قیمت
        queryset = queryset.annotate(
            min_price=Min("color_inventories__price"),
            max_price=Max("color_inventories__price")
        )

        # annotate برای اولویت قیمت (برای همه حالت‌ها)
        queryset = queryset.annotate(
            price_priority=Case(
                When(min_price__isnull=True, then=Value(1)),
                When(min_price=0, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )

        # فیلتر مرتب‌سازی
        order_by = self.request.GET.get("order_by")
        if order_by == "visited":
            queryset = queryset.order_by("price_priority", F("product_view").desc(nulls_last=True))
        elif order_by == "newest":
            queryset = queryset.order_by("price_priority", F("created_date").desc(nulls_last=True))
        elif order_by == "popular":
            queryset = queryset.order_by("price_priority", F("avg_rate").desc(nulls_last=True))
        elif order_by == "cheap":
            queryset = queryset.order_by("price_priority", "min_price")
        elif order_by == "expensive":
            queryset = queryset.order_by("price_priority", "-max_price")
        else:
            # اگر کاربر order_by نفرستاده بود، فقط اولویت قیمت مهم است
            queryset = queryset.order_by("price_priority")

        # محاسبه تخفیف
        discounted_price_expr = ExpressionWrapper(
            F('price') - (F('price') * F('discount_percent') / 100),
            output_field=DecimalField()
        )

        discounted_inventory = ProductColorInventory.objects.filter(
            product=OuterRef('pk')
        ).annotate(
            discounted_price=discounted_price_expr
        ).filter(
            discounted_price__gt=0
        ).order_by('discounted_price')

        queryset = queryset.annotate(
            min_discounted_price=Subquery(discounted_inventory.values('discounted_price')[:1]),
            min_discount_percent=Subquery(discounted_inventory.values('discount_percent')[:1])
        )

        # prefetch رنگ‌ها
        queryset = queryset.prefetch_related(
            Prefetch('color_inventories', queryset=ProductColorInventory.objects.select_related('color'))
        )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.get_queryset().count()
        context["categories"] = ProductCategoryModel.objects.all()
        context["brands"] = Brand.objects.all()
        context["selected_brands"] = self.request.GET.getlist("brand")
        context["selected_categories"] = self.request.GET.getlist("category")
        context["selected_order"] = self.request.GET.get("order_by", "")
        price_range = ProductColorInventory.objects.filter(price__gt=0).aggregate(
        min_price=Min("price"),
        max_price=Max("price")
        )
        context["min_price_all"] = price_range["min_price"]
        context["max_price_all"] = price_range["max_price"]

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

        # فیلتر رنگ‌هایی که قیمت تخفیف‌خورده آن‌ها بزرگ‌تر از صفر است
        valid_colors = [color for color in colors if color.discounted_price > 0]

        # پیدا کردن رنگ با کمترین قیمت تخفیف‌خورده (بزرگ‌تر از صفر)
        default_color = min(valid_colors, key=lambda c: c.discounted_price, default=None)
        product_users_count = CartItemModel.objects.filter(product=product).values('cart__user').distinct().count()

        context['colors'] = colors
        context['default_color'] = default_color
        context['specifications'] = ProductSpecification.objects.filter(product=product)
        context["is_wished"] = WishlistProductModel.objects.filter(
            user=self.request.user, product__id=self.get_object().id).exists() if self.request.user.is_authenticated else False
        reviews = ReviewModel.objects.filter(product=product,status=ReviewStatusType.accepted.value)
        context["reviews"] = reviews
        total_reviews_count =reviews.count()
        context["total_reviews_count"] = total_reviews_count
        context['product_view_times_100'] = product.product_view * 10
        context['product_in_cart_users_count'] = product_users_count
        return context
     
 
  
class AddOrRemoveWishlistView(LoginRequiredMixin, View):


    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        message = ""
        if product_id:
            try:
                wishlist_item = WishlistProductModel.objects.get(
                    user=request.user, product__id=product_id)
                wishlist_item.delete()
                message = "محصول از لیست علایق حذف شد"
            except WishlistProductModel.DoesNotExist:
                WishlistProductModel.objects.create(
                    user=request.user, product_id=product_id)
                message = "محصول به لیست علایق اضافه شد"

        return JsonResponse({"message": message})