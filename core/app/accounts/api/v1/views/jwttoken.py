from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers import CustomTokenObtainSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer