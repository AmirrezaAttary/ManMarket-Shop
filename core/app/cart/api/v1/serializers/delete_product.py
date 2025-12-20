from rest_framework import serializers
from ....models import CartItemModel

class CartItemDeleteProduct(serializers.ModelSerializer):

    class Meta:
        model = CartItemModel
        fields = [
            "id",
        ]