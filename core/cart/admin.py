from cart.models import CartItemModel, CartModel
from django.contrib import admin

@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user")


@admin.register(CartItemModel)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ("id", "cart","product","quantity")