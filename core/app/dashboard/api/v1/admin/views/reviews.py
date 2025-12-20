from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from app.review.models import ReviewModel
from app.dashboard.api.v1.admin.paginations import LargeResultsSetPagination
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser
from app.dashboard.api.v1.admin.serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = ReviewModel.objects.all()
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["created_date", "status"]
    search_fields = ["id", "user__phone_number", "user__email"]
    ordering_fields = ["created_date", "status", "rate"]

    # فقط متدهای GET، PUT و PATCH مجاز هستند
    http_method_names = ["get", "put", "patch"]

    # در صورت تمایل می‌توان create را هم غیرفعال کرد برای اطمینان بیشتر
    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "ایجاد نظر از طریق این مسیر مجاز نیست."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
