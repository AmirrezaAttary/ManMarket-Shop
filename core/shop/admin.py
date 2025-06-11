from django.contrib import admin
from django.utils.html import format_html

from .models import (ProductModel,
                    ProductCategoryModel,
                    ProductImageModel,
                    Color,
                    ProductColorInventory,
                    ProductSpecification ,
                    Brand,
                    WishlistProductModel
                    )

# ثبت رنگ‌ها به صورت مستقل
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("id", "title")

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ("name", "value")

# اینلاین رنگ و قیمت برای محصولات
class ProductColorInventoryInline(admin.TabularInline):
    model = ProductColorInventory
    extra = 1
    autocomplete_fields = ("color",)
    fields = ("color", "price", "stock", "discount_percent",'hex_color')
    readonly_fields = ()

# مدیریت محصولات
@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_date","product_view")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductSpecificationInline,ProductColorInventoryInline]
    list_filter = ("status", "category", "brand")
    list_per_page = 20

# مدیریت دسته‌بندی محصولات
@admin.register(ProductCategoryModel)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    
# مدیریت برند محصولات
@admin.register(Brand)
class ProductBrandModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

# مدیریت عکس‌های اضافی محصولات
@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "thumbnail_preview", "file", "created_date")
    search_fields = ("file",)
    list_per_page = 20

    def thumbnail_preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" width="20" height="20" style="object-fit: cover; border-radius: 6px;" />', obj.file.url)
        return "-"
    thumbnail_preview.short_description = "Preview"  # عنوان ستون
    
    
    

@admin.register(WishlistProductModel)
class WishlistProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")
