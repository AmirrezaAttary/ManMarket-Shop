from rest_framework.generics import RetrieveUpdateAPIView
from ....models import CartItemModel
from ..serializers import CartItemAddProductSerializers
from ..permissions import IsCustomer

class CartUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = CartItemAddProductSerializers
    # permission_classes = [IsCustomer]
    queryset = CartItemModel.objects.all()
