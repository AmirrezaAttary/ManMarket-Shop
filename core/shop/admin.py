from django.contrib import admin
from .models import ProductModel, ProductCategoryModel, ProductImageModel, Color, ProductColorInventory

# ثبت رنگ‌ها به صورت مستقل
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("id", "title")

# اینلاین رنگ و قیمت برای محصولات
class ProductColorInventoryInline(admin.TabularInline):
    model = ProductColorInventory
    extra = 1
    autocomplete_fields = ("color",)
    fields = ("color", "price", "stock", "discount_percent")
    readonly_fields = ()

# مدیریت محصولات
@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_date")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductColorInventoryInline]
    list_filter = ("status", "category")
    list_per_page = 20

# مدیریت دسته‌بندی محصولات
@admin.register(ProductCategoryModel)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

# مدیریت عکس‌های اضافی محصولات
@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created_date")
    search_fields = ("file",)