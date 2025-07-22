from cart.models import CartItemModel, CartModel
from django.contrib import admin

@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("id", "user__email")


@admin.register(CartItemModel)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ("id", "cart","product","quantity")
    search_fields = ('id','product__id','product__title')