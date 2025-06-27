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
        status=ProductStatusType.publish.value
    ).annotate(
        discount=F('color_inventories__price') * (F('color_inventories__discount_percent') / 100)
    ).order_by('-discount')[:16]

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
        status=ProductStatusType.publish.value
    ).order_by('-sales_count')[:16]

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
        status=ProductStatusType.publish.value
    ).order_by('-product_view')[:16]

    wishlist_items = WishlistProductModel.objects.filter(user=request.user).values_list("product__id", flat=True) if request.user.is_authenticated else []

    return {
        "latest_products": most_viewed_products,
        "request": request,
        "wishlist_items": wishlist_items
    }