from rest_framework import viewsets,mixins

from ......wallets.models import WalletTransaction
from app.dashboard.api.v1.user.serializers.wallet import WalletSerializer,WalletTransactionSerializer
from app.dashboard.api.v1.user.permissions import IsCustomer
from app.dashboard.api.v1.user.paginations import LargeResultsSetPagination

class WalletViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WalletSerializer
    permission_classes = [IsCustomer]

    def get_object(self):
        return self.request.user.wallet_user
    

class WalletTransactionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsCustomer]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return WalletTransaction.objects.filter(
            wallet=self.request.user.wallet_user
        ).order_by("-created_at")