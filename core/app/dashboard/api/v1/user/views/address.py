from rest_framework import viewsets
from app.order.models import UserAddressModel
from app.dashboard.api.v1.user.serializers import UserAddressModelSerializers
from app.dashboard.api.v1.user.permissions import IsCustomer
from app.dashboard.api.v1.user.paginations import LargeResultsSetPagination

class UserAddressModelViewSet(viewsets.ModelViewSet):
    serializer_class = UserAddressModelSerializers
    permission_classes = [IsCustomer]
    pagination_class = LargeResultsSetPagination
    

    def get_queryset(self):
        user = self.request.user
        return UserAddressModel.objects.filter(user=user).order_by('-created_date')