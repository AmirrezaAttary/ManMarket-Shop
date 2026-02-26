from rest_framework import serializers
from ....models import CartItemModel, CartModel

class CartItemAddProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartItemModel
        fields = [
            "cart",
            "product",
            "color",
            "color_inventory",
            "quantity",
        ]
        read_only_fields = ["cart"]

    def create(self, validated_data):
        user = self.context["request"].user

        # پیدا یا ساخت سبد خرید برای کاربر فعلی
        cart, _ = CartModel.objects.get_or_create(user=user)

        product = validated_data.get("product")
        color_inventory = validated_data.get("color_inventory")
        quantity = validated_data.get("quantity", 1)

        # بررسی اینکه آیا محصول با همین رنگ از قبل در سبد خرید هست یا نه
        existing_item = CartItemModel.objects.filter(
            cart=cart, product=product, color_inventory=color_inventory
        ).first()

        if existing_item:
            # افزایش تعداد محصول
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item  # بازگرداندن آیتم به‌روزشده

        # در غیر این صورت، ساخت آیتم جدید
        validated_data["cart"] = cart
        return super().create(validated_data)
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("تعداد محصول باید حداقل ۱ باشد.")
        return value