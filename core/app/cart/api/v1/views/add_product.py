from rest_framework.generics import CreateAPIView
from ....models import CartItemModel
from ..serializers import CartItemAddProductSerializers

class CartAddProductCreateAPIView(CreateAPIView):
    serializer_class = CartItemAddProductSerializers
    # permission_classes = [IsCustomer]
    queryset = CartItemModel.objects.all()
