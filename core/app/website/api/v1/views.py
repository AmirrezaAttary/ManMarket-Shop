from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import (
    Banner,
    FAQ,
    SiteSetting,
)
from .serializers import (
    BannerSerializer,
    FAQSerializer,
    SiteSettingSerializer,
)


class SiteSettingAPIView(APIView):
    """GET /website/v1/site-setting/ — تنظیمات کلی سایت (لوگو، تماس، شبکه‌های اجتماعی، اعلان و ...)"""

    permission_classes = [AllowAny]

    def get(self, request):
        data = SiteSettingSerializer(SiteSetting.load(), context={"request": request}).data
        return Response(data)


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /website/v1/banners/?position=1 — فقط بنرهای فعالِ داخل بازه‌ی زمانی نمایش"""

    serializer_class = BannerSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        now = timezone.now()
        qs = Banner.objects.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now),
        )
        position = self.request.query_params.get("position")
        if position and position.isdigit():
            qs = qs.filter(position=int(position))
        return qs


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /website/v1/faq/?category=3"""

    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = FAQ.objects.filter(is_active=True)
        category = self.request.query_params.get("category")
        if category and category.isdigit():
            qs = qs.filter(category=int(category))
        return qs
