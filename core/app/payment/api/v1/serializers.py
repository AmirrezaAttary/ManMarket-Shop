from rest_framework import serializers
from ...models import PaymentModel


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentModel
        fields = [
            "id",
            "authority_id",
            "ref_id",
            "amount",
            "response_json",
            "response_code",
            "status",
            "payemnt_type",
            "remainder",
            "wallet",
            "order",
        ]

