from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from app.dashboard.api.v1.user.permissions import IsCustomer
from app.dashboard.api.v1.user.serializers import UserChangePasswordSerializer


class UserSecurityViewSet(viewsets.ViewSet):
    """
    🔐 تغییر رمز عبور ادمین (با فرم HTML در DRF Browsable API)
    """
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsCustomer]
    http_method_names = ['get', 'post']

    def list(self, request):
        return Response({
            "message": "برای تغییر رمز عبور از متد POST استفاده کنید.",
            "fields": {
                "old_password": "رمز فعلی",
                "new_password": "رمز جدید",
                "confirm_password": "تکرار رمز جدید"
            }
        })

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.password = make_password(serializer.validated_data['new_password'])
        user.save()

        if hasattr(user, 'auth_token'):
            user.auth_token.delete()

        return Response({"detail": "رمز عبور با موفقیت تغییر کرد ✅"}, status=status.HTTP_200_OK)
