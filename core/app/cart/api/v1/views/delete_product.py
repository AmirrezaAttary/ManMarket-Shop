from rest_framework.generics import RetrieveDestroyAPIView
from ....models import CartItemModel
from ..serializers import CartItemDeleteProduct
from ..permissions import IsCustomer

class CartItemDestroyAPIView(RetrieveDestroyAPIView):
    serializer_class = CartItemDeleteProduct
    # permission_classes = [IsCustomer]
    queryset = CartItemModel.objects.all()