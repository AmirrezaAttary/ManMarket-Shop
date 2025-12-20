from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from app.shop.models.brands import Brand
from app.dashboard.api.v1.admin.paginations import LargeResultsSetPagination
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser
from app.dashboard.api.v1.admin.serializers import BrandSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = BrandSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_date"]

