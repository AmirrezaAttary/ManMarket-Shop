# carts/views.py
from rest_framework.generics import (
    RetrieveAPIView,
)
from ....models import CartModel
from ..serializers import (
    CartSerializer,
)
from ..permissions import IsCustomer
from rest_framework.permissions import IsAuthenticated

class CartRetrieveAPIView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartModel.objects.filter(user=self.request.user)

    def get_object(self):
        cart, created = CartModel.objects.get_or_create(user=self.request.user)
        return cart


