from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from app.shop.models import Color   
from app.dashboard.api.v1.admin.serializers import  ColorSerializer
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser
    

class ColorViewSet(viewsets.ModelViewSet):
    
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAdminOrSuperUser]
    search_fields = ["title", "hex_color"]
    ordering_fields = ["id"]

