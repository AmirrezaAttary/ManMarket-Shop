from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from app.accounts.models import UserType


class DashboardHomeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.type == UserType.customer.value:
            return redirect('/dashboard/v1/user/')

        if user.type in [UserType.admin.value, UserType.superuser.value]:
            return redirect('/dashboard/v1/admin/')

        return Response({"detail": "User type not recognized."}, status=400)
