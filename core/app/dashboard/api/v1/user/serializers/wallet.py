from rest_framework import serializers
from ......wallets.models import Wallet,WalletTransaction


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ["id", "balance"]
        read_only_fields = fields


class WalletTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "amount",
            "created_at",
            "description",
            "transaction_type",
        ]
        read_only_fields = fields
