from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from app.shop.models import ProductColorInventory
from app.dashboard.api.v1.admin.serializers import InventorySerializer
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser

class InventoryViewSet(viewsets.ModelViewSet):
    
    queryset = ProductColorInventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAdminOrSuperUser]
    search_fields = ["color__title", "color__hex_color"]
    ordering_fields = ["id", "price", "final_price", "stock", "updated_date"]
