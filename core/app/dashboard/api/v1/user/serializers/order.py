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

    class Meta:
        model = OrderModel
        fields = '__all__'

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