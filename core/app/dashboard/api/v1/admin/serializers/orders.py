from rest_framework import serializers
from app.order.models import OrderModel


class AdminOrderSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = OrderModel
        fields = [
            "user",
            "address",
            "state",
            "city",
            "zip_code",
            "payment",
            "total_price",
            "coupon",
            "status",
            "created_date",
            "updated_date",
            "tracking_type",
            "tracking_code",
            "absolute_url"
        ]
        read_only_fields = [
            "user",
            "address",
            "state",
            "city",
            "zip_code",
            "payment",
            "total_price",
            "coupon",
            "created_date",
            "updated_date",
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)
        else:
            rep.pop("address", None)
            rep.pop("state", None)
            rep.pop("city", None)
            rep.pop("zip_code", None)
            rep.pop("payment", None)
            rep.pop("couponmodels", None)
            rep.pop("tracking_type", None)
            rep.pop("tracking_code", None)

        return rep

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return f"{request.build_absolute_uri(obj.pk)}/"