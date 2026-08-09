# carts/serializers.py
from rest_framework import serializers
from ....models import CartModel, CartItemModel


class CartItemSerializerCart(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    color_name = serializers.CharField(source="color.name", read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = CartItemModel
        fields = [
            "id",
            "product",
            "product_slug",
            "product_title",
            "color_name",
            "color_inventory",
            "quantity",
            "price",
        ]

    def get_price(self, obj):
        return obj.color_inventory.get_price() * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializerCart(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartModel
        fields = ["id", "user", "cart_items", "total_price", "created_date"]
        read_only_fields = ["user",]

    def get_total_price(self, obj):
        return obj.calculate_total_price()
    
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
