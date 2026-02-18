from rest_framework import viewsets
from app.shop.models import WishlistProductModel
from app.dashboard.api.v1.user.serializers import WishlistProductModelSerializers
from app.dashboard.api.v1.user.permissions import IsCustomer
from app.dashboard.api.v1.user.paginations import LargeResultsSetPagination

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistProductModelSerializers
    permission_classes = [IsCustomer]
    pagination_class = LargeResultsSetPagination
    # http_method_names = ['get', 'head', 'options','delete']

    def get_queryset(self):
        user = self.request.user
        return WishlistProductModel.objects.filter(user=user).order_by('-id')