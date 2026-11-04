from django.contrib import admin
from .models import OrderModel, OrderItemModel, CouponModel, UserAddressModel

# Register your models here.


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "phone_number",
        "total_price",
        "coupon",
        "status",
        "created_date",
        "tracking_type",
        "tracking_code",
    )


@admin.register(OrderItemModel)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "created_date"
    )


@admin.register(CouponModel)
class CouponModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_type",
        "discount_percent",
        "max_discount_amount",
        "discount_amount",
        "min_order_amount",
        "is_active",
        "max_limit_usage",
        "used_by_count",
        "expiration_date",
        "created_date"
    )
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)

    def used_by_count(self, obj):
        return obj.used_by.all().count()


@admin.register(UserAddressModel)
class UserAddressModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "phone_number",
        "state",
        "city",
        "zip_code",
        "created_date"
    )