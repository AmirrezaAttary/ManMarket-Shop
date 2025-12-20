from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from app.blog.models import Post,Category
from app.dashboard.api.v1.admin.paginations import LargeResultsSetPagination
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser
from app.dashboard.api.v1.admin.serializers import PostSerializer,DashboardPostCategorySerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = PostSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_date"]
    
    
class PostCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = DashboardPostCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name","slug"]
    ordering_fields = ["id"]
    