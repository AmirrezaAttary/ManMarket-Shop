from django.contrib import admin
from django.utils.html import format_html

from .models import (ProductModel,
                    ProductCategoryModel,
                    ProductImageModel,
                    Color,
                    ProductColorInventory,
                    ProductSpecification ,
                    Brand,
                    WishlistProductModel,
                    MegaMenu,
                    ProductQuestion,
                    )

# ثبت رنگ‌ها به صورت مستقل
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("id", "title")

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ("name", "value",'status')

# اینلاین رنگ و قیمت برای محصولات
class ProductColorInventoryInline(admin.TabularInline):
    model = ProductColorInventory
    extra = 1
    autocomplete_fields = ("color",)
    fields = ("color", "price", "stock","final_price", "discount_percent", "hex_color", "updated_date")
    readonly_fields = ("updated_date",)

# مدیریت محصولات
@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_date","product_view")
    search_fields = ("title","id",)
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
    thumbnail_preview.short_description = "پیش‌نمایش"  # عنوان ستون
    
    
    

@admin.register(WishlistProductModel)
class WishlistProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")


@admin.register(MegaMenu)
class MegaMenuAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "brand", "created_date", "updated_date")
    search_fields = ("category__title", "brand__title")
    list_filter = ("category", "brand")
    list_per_page = 20


@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "short_question", "status", "created_date")
    list_filter = ("status",)
    search_fields = ("question", "answer", "product__title", "user__phone_number")
    list_per_page = 20
    autocomplete_fields = ("product",)
    raw_id_fields = ("user",)
    actions = ("approve_selected", "reject_selected")

    @admin.display(description="پرسش")
    def short_question(self, obj):
        return (obj.question[:60] + "…") if len(obj.question) > 60 else obj.question

    @admin.action(description="تایید پرسش‌های انتخاب‌شده")
    def approve_selected(self, request, queryset):
        updated = queryset.update(status=2)
        self.message_user(request, f"{updated} پرسش تایید شد.")

    @admin.action(description="رد پرسش‌های انتخاب‌شده")
    def reject_selected(self, request, queryset):
        updated = queryset.update(status=3)
        self.message_user(request, f"{updated} پرسش رد شد.")
