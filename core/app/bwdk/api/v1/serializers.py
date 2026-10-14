from rest_framework import serializers


class CartLineSerializer(serializers.Serializer):
    color_inventory = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=50)


class CreateCheckoutSerializer(serializers.Serializer):
    # Guests send their local cart. Logged-in users may omit it: their saved cart is used.
    items = CartLineSerializer(many=True, required=False)


class CompleteSerializer(serializers.Serializer):
    merchant_unique_id = serializers.CharField(max_length=255)
    edit_basket = serializers.BooleanField(required=False, default=False)


class RefundSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255, required=False, default="انصراف مشتری از خرید")
