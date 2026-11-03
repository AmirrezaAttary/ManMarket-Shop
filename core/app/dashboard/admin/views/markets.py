from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse
from django.views.generic import TemplateView

from ....bwdk.models import BWDKOrder
from ....digify.feed import feed_queryset
from ....shop.models import ProductColorInventory, ProductModel, ProductStatusType
from ...permissions import HasAdminAccessPermission


class AdminMarketsView(LoginRequiredMixin, HasAdminAccessPermission, TemplateView):
    """وضعیت اتصال به دیجی‌فای (فید کاتالوگ)، ترب و خرید با دیجی‌کالا (BWDK) — فقط نمایشی و بدون نمایش کلیدها."""

    template_name = "dashboard/admin/markets/markets.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        req = self.request

        feed_total = feed_queryset().count()
        published = ProductModel.objects.filter(status=ProductStatusType.publish.value).count()
        in_stock = (
            ProductModel.objects.filter(
                status=ProductStatusType.publish.value,
                color_inventories__stock__gt=0,
                color_inventories__price__gt=0,
            )
            .distinct()
            .count()
        )
        ctx["digify"] = {
            "list_url": req.build_absolute_uri(reverse("digify:product-list")),
            "detail_url": req.build_absolute_uri(reverse("digify:product-detail", kwargs={"pk": 1})).replace("/1/", "/{id}/"),
            "protected": bool(getattr(settings, "DIGIFY_FEED_API_KEY", "")),
            "allowed_ips": getattr(settings, "DIGIFY_FEED_ALLOWED_IPS", []),
            "site_url": getattr(settings, "DIGIFY_SITE_URL", ""),
            "media_url": getattr(settings, "DIGIFY_MEDIA_BASE_URL", ""),
            "default_limit": getattr(settings, "DIGIFY_FEED_DEFAULT_LIMIT", 100),
            "max_limit": getattr(settings, "DIGIFY_FEED_MAX_LIMIT", 200),
            "feed_total": feed_total,
            "published": published,
            "in_stock": in_stock,
        }
        ctx["torob"] = {
            "url": req.build_absolute_uri("/torob_api/v3/products"),
            "audiences": getattr(settings, "TOROB_ALLOWED_AUDIENCES", []),
            "site_url": getattr(settings, "TOROB_SITE_URL", ""),
        }
        ctx["bwdk"] = {
            "env": getattr(settings, "BWDK_ENV", ""),
            "key_set": bool(getattr(settings, "BWDK_API_KEY", "")),
            "callback_base": getattr(settings, "BWDK_CALLBACK_BASE", ""),
            "reservation_minutes": getattr(settings, "BWDK_RESERVATION_MINUTES", ""),
            "stats": BWDKOrder.objects.aggregate(
                total=Count("id"),
                open=Count("id", filter=Q(finalized_at__isnull=True, cancelled_at__isnull=True)),
                needs_review=Count("id", filter=Q(needs_review=True)),
            ),
        }
        return ctx
