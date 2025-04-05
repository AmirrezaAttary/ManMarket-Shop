from django.contrib import admin
from .models import (
    ProductModel,
    ProductCategoryModel,
    ProductImageModel,
    ProductColor,
    ProductColorVariant,
    )
# Register your models here.

class ProductColorVariantInline(admin.TabularInline):
    model = ProductColorVariant
    extra = 1

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    inlines = [ProductColorVariantInline]
    list_display = ("id", "title", "price", "discount_percent", "status")

admin.site.register(ProductColor)
@admin.register(ProductCategoryModel)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date")

@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created_date")

