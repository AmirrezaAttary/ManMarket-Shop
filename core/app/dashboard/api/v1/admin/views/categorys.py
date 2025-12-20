from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from app.shop.models.categorys import ProductCategoryModel
from app.dashboard.api.v1.admin.paginations import LargeResultsSetPagination
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser
from app.dashboard.api.v1.admin.serializers import AdminCategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategoryModel.objects.all()
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = AdminCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_date"]
