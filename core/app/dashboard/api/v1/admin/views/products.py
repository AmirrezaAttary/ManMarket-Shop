from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from app.shop.models import ProductModel
from app.dashboard.api.v1.admin.paginations import LargeResultsSetPagination
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser
from app.dashboard.api.v1.admin.filterset import ProductFilter
from app.dashboard.api.v1.admin.serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    
    queryset = ProductModel.objects.all()
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title"]
    ordering_fields = ["created_date"]