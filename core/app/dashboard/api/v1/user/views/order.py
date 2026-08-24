from rest_framework import viewsets
from app.order.models import OrderModel
from app.dashboard.api.v1.user.serializers import UserOrderSerializer
from app.dashboard.api.v1.user.permissions import IsCustomer
from app.dashboard.api.v1.user.paginations import LargeResultsSetPagination

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = UserOrderSerializer
    permission_classes = [IsCustomer]
    pagination_class = LargeResultsSetPagination
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = OrderModel.objects.filter(user=user).order_by('-created_date')
        if self.action == 'retrieve':
            qs = qs.prefetch_related(
                'order_items__product',
                'order_items__color',
            ).select_related('payment', 'coupon')
        return qs