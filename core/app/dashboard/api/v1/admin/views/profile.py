# app/accounts/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import redirect
from app.accounts.models import Profile
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser
from app.dashboard.api.v1.admin.serializers import AdminProfileSerializer



class AdminProfileViewSet(viewsets.ModelViewSet):
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAdminOrSuperUser]
    http_method_names = ['get', 'put', 'patch']

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    """def list(self, request, *args, **kwargs):
        profile = self.get_queryset().first()
        if not profile:
            profile = Profile.objects.create(user=request.user)
        url = request.build_absolute_uri(f'{request.path}{profile.id}/')
        return Response({"detail": "redirect_to_update", "url": url}, status=status.HTTP_303_SEE_OTHER)"""


    def list(self, request, *args, **kwargs):
        profile = self.get_queryset().first()
        if not profile:
            profile = Profile.objects.create(user=request.user)
        # ریدایرکت واقعی به صفحه آپدیت (برای مرورگر)
        return redirect(f'{request.path}{profile.id}/')

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_queryset().first()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # اگر پروفایل ندارد، بسازد، اگر دارد، خطا ندهد
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        profile = self.get_queryset().first()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)