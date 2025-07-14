from django import template
from shop.models import ProductStatusType, ProductModel, WishlistProductModel

from django.db.models import F
register = template.Library()

@register.inclusion_tag("includes/latest-product.html", takes_context=True)
def show_latest_products(context):
    request = context.get("request")
    latest_products = ProductModel.objects.filter(
        status=ProductStatusType.publish.value
    ).distinct().order_by("-created_date")[:16]
    
    wishlist_items = WishlistProductModel.objects.filter(user=request.user).values_list("product__id", flat=True) if request.user.is_authenticated else []
    
    return {
        "latest_products": latest_products,
        "request": request,
        "wishlist_items": wishlist_items
    }



@register.inclusion_tag("includes/highest-discount-products.html", takes_context=True)
def show_highest_discount_products(context):
    request = context.get("request")
    highest_discount_products = ProductModel.objects.filter(
        status=ProductStatusType.publish.value,
        color_inventories__price__gt=0  # فیلتر محصولات دارای قیمت مثبت
    ).annotate(
        discount=F('color_inventories__price') * (F('color_inventories__discount_percent') / 100)
    ).order_by('-discount').distinct()[:16]  # distinct برای جلوگیری از تکرار محصول به‌خاطر رابطه many-to-one

    wishlist_items = WishlistProductModel.objects.filter(user=request.user).values_list("product__id", flat=True) if request.user.is_authenticated else []

    return {
        "latest_products": highest_discount_products,
        "request": request,
        "wishlist_items": wishlist_items
    }


@register.inclusion_tag("includes/highest-sales-products.html", takes_context=True)
def show_highest_sales_products(context):
    request = context.get("request")
    highest_sales_products = ProductModel.objects.filter(
        status=ProductStatusType.publish.value,
        color_inventories__price__gt=0
    ).order_by('-sales_count').distinct()[:16]

    wishlist_items = WishlistProductModel.objects.filter(user=request.user).values_list("product__id", flat=True) if request.user.is_authenticated else []

    return {
        "latest_products": highest_sales_products,
        "request": request,
        "wishlist_items": wishlist_items
    }



@register.inclusion_tag("includes/most-viewed-products.html", takes_context=True)
def show_most_viewed_products(context):
    request = context.get("request")
    most_viewed_products = ProductModel.objects.filter(
        status=ProductStatusType.publish.value,
        color_inventories__price__gt=0
    ).order_by('-product_view').distinct()[:16]

    wishlist_items = WishlistProductModel.objects.filter(user=request.user).values_list("product__id", flat=True) if request.user.is_authenticated else []

    return {
        "latest_products": most_viewed_products,
        "request": request,
        "wishlist_items": wishlist_items
    }



@register.inclusion_tag("includes/similar-products.html", takes_context=True)
def show_similar_products(context, product):
    request = context.get("request")
    brand = product.brand
    # category = product.category

    similar_prodcuts = ProductModel.objects.filter(
        status=ProductStatusType.publish.value,
        brand=brand,
        # category=category,
        color_inventories__price__gt=0  # فقط محصولاتی که حداقل یک قیمت > 0 دارند
    ).exclude(id=product.id).distinct().order_by("-created_date")

    wishlist_items = WishlistProductModel.objects.filter(
        user=request.user
    ).values_list("product__id", flat=True) if request.user.is_authenticated else []

    return {
        "similar_prodcuts": similar_prodcuts,
        "request": request,
        "wishlist_items": wishlist_items
    }