from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ...models import ReviewModel
from .serialaizer import ReviewSerializers
from .permissions import IsCustomer

class ReviewViewsets(viewsets.ModelViewSet):
    queryset = ReviewModel.objects.all()
    serializer_class = ReviewSerializers
    permission_classes = [IsCustomer]
    http_method_names = ["get","post","head","options"]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["product__title"]
    ordering_fields = ["created_date",]