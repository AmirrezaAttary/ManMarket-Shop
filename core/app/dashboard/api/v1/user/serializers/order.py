from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from app.order.models import OrderModel, OrderItemModel
from app.shop.models import ProductModel, Color  # مسیر رو با ساختار پروژه‌ت چک کن


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ["id", "title", "slug", "image"]


class OrderItemColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "title", "hex_color"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)
    color = OrderItemColorSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemModel
        fields = [
            "id",
            "product",
            "color",
            "quantity",
            "price",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.price * obj.quantity


class UserOrderSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    items = OrderItemSerializer(source="order_items", many=True, read_only=True)
    status_detail = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    tracking_url = serializers.SerializerMethodField()
    can_retry_payment = serializers.SerializerMethodField()
    payment_expires_at = serializers.SerializerMethodField()
    remaining_payment_seconds = serializers.SerializerMethodField()

    class Meta:
        model = OrderModel
        fields = '__all__'

    def get_can_retry_payment(self, obj):
        if obj.status != 1:
            return False

        expires_at = obj.created_date + timedelta(minutes=30)
        if timezone.now() >= expires_at:
            return False

        for item in obj.order_items.all():
            inventory = item.product.color_inventories.filter(
                color_id=item.color_id
            ).first()
            if not inventory or inventory.stock < item.quantity:
                return False

        return True

    def get_payment_expires_at(self, obj):
        if obj.status != 1:
            return None
        return obj.created_date + timedelta(minutes=30)

    def get_remaining_payment_seconds(self, obj):
        if obj.status != 1:
            return 0
        expires_at = obj.created_date + timedelta(minutes=30)
        return max(0, int((expires_at - timezone.now()).total_seconds()))

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        is_detail = bool(request.parser_context.get("kwargs", {}).get("pk"))

        if is_detail:
            rep.pop("absolute_url", None)
        else:
            # تو لیست، جزئیات آیتم‌ها و آدرس کامل رو نشون نده
            rep.pop("items", None)
            rep.pop("full_address", None)

        return rep

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"

    def get_status_detail(self, obj):
        return obj.get_status()

    def get_final_price(self, obj):
        return obj.get_price()

    def get_full_address(self, obj):
        return obj.get_full_address()

    def get_tracking_url(self, obj):
        return obj.get_tracking_url()