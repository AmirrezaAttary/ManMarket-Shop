from rest_framework import serializers
from ...models import OrderModel,OrderItemModel,TrackingType,UserAddressModel,CouponModel


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderModel
        fields = [
            "id",
            "user",
            "address",
            "state",
            "city",
            "zip_code",
            "payment",
            "total_price",
            "coupon",
            "tracking_type",
        ]
        read_only_fields = ["user",]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
    
class OrderItemSerializers(serializers.ModelSerializer):

    class Meta:
        model = OrderItemModel
        fields = [
            "order",
            "product",
            "color",
            "quantity",
            "price",
        ]


class OrderCheckOutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    coupon = serializers.CharField(required=False, allow_blank=True)
    tracking_type = serializers.ChoiceField(choices=[(tag.value, tag.label) for tag in TrackingType])

    def validate_address_id(self, value):
        user = self.context['request'].user
        if not UserAddressModel.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("آدرس انتخاب شده معتبر نیست.")
        return value

    def validate_coupon(self, value):
        if value:
            if not CouponModel.objects.filter(code=value).exists():
                raise serializers.ValidationError("کوپن وارد شده معتبر نیست.")
        return value