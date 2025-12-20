from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from app.shop.models import ProductImageModel
from app.dashboard.api.v1.admin.serializers import ProductImageCreateSerializer
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser

class ProductImageViewSet(viewsets.ModelViewSet):
    
    queryset = ProductImageModel.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    serializer_class = ProductImageCreateSerializer
    permission_classes = [IsAdminOrSuperUser]
    search_fields = ["product", "color"]
    ordering_fields = ["created_date"]