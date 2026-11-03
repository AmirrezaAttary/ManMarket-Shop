import hashlib
import hmac
import logging
from uuid import UUID

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from app.accounts.models import UserType
from app.dashboard.api.v1.admin.permissions import IsAdminOrSuperUser

from ...authentication import OptionalJWTAuthentication
from ...client import BWDKError
from ...models import BWDKOrder
from ...services import BWDKService
from .serializers import (
    CompleteSerializer,
    CreateCheckoutSerializer,
    RefundSerializer,
)


log = logging.getLogger("bwdk")


def _is_admin(user):
    return user.is_authenticated and user.type in (UserType.admin, UserType.superuser)


class BWDKCreateOrderAPIView(APIView):
    """POST /bwdk/v1/create/

    Login is NOT required (Digikala express checkout). Guests send {"items": [...]}; logged-in
    users can omit items and their saved cart is used. The stock is reserved for the payment window.
    """

    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "bwdk-create"

    def post(self, request):
        serializer = CreateCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            bw = BWDKService().create_checkout(
                user=request.user,
                items=serializer.validated_data.get("items"),
                request=request,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(
            {"order_id": bw.order_id, "order_start_url": bw.order_start_url},
            status=201,
        )


class BWDKCompleteAPIView(APIView):
    """POST /bwdk/v1/complete/  {merchant_unique_id, edit_basket?}

    Called by the Next.js callback page (/bwdk/callback/<id>). The callback query-string is not
    trusted: Get Order decides. Idempotent, so the page can poll while Verify is pending.
    """

    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "bwdk-complete"

    def post(self, request):
        serializer = CompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = BWDKService().complete(
                serializer.validated_data["merchant_unique_id"],
                edit_basket=serializer.validated_data["edit_basket"],
            )
        except BWDKOrder.DoesNotExist:
            return Response({"detail": "سفارش پیدا نشد."}, status=404)
        return Response(result)


class _OwnerOrAdminMixin:
    def get_bwdk_order(self, request, order_uuid):
        bw = get_object_or_404(BWDKOrder.objects.select_related("order"), order_uuid=order_uuid)
        if bw.order.user_id != request.user.id and not _is_admin(request.user):
            self.permission_denied(request)
        return bw


class BWDKGetOrderAPIView(_OwnerOrAdminMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_uuid):
        bw = self.get_bwdk_order(request, order_uuid)
        try:
            data = BWDKService().client.get_order(bw.order_uuid)
        except BWDKError as exc:
            return Response({"detail": exc.detail}, status=502)
        return Response(data)


class BWDKVerifyOrderAPIView(_OwnerOrAdminMixin, APIView):
    """Manual Verify. Always Get Order first, Verify only when status == 7 (done by the service)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, order_uuid):
        bw = self.get_bwdk_order(request, order_uuid)
        bw = BWDKService().manual_verify(bw)
        return Response(BWDKService.result_for(bw))


class BWDKRefundOrderAPIView(APIView):
    """Admins only. Full refund, Digipay payments only."""

    permission_classes = [IsAdminOrSuperUser]

    def post(self, request, order_uuid):
        bw = get_object_or_404(BWDKOrder, order_uuid=order_uuid)
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            bw = BWDKService().refund(bw, serializer.validated_data["reason"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"status": bw.status, "status_display": bw.status_display})


# Headers in which a webhook secret / signature may arrive (Django META names).
_SIGNATURE_HEADERS = (
    "HTTP_X_SIGNATURE",
    "HTTP_X_WEBHOOK_SIGNATURE",
    "HTTP_X_WEBHOOK_SECRET",
    "HTTP_X_HUB_SIGNATURE_256",
    "HTTP_AUTHORIZATION",
)


def _webhook_signature_ok(request):
    """True when the request carries our secret, either as an HMAC-SHA256 of the raw body or as the
    plain secret (optionally prefixed with sha256= / Bearer / Api-Key). No secret configured => reject."""
    secret = getattr(settings, "BWDK_WEBHOOK_SECRET", "") or ""
    if not secret:
        return False
    extra = getattr(settings, "BWDK_WEBHOOK_SIGNATURE_HEADER", "")
    headers = ((extra,) if extra else ()) + _SIGNATURE_HEADERS
    expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    for name in headers:
        value = (request.META.get(name) or "").strip()
        if not value:
            continue
        for prefix in ("sha256=", "Bearer ", "Api-Key ", "bearer ", "api-key "):
            if value.startswith(prefix):
                value = value[len(prefix):].strip()
        if hmac.compare_digest(value.lower(), expected) or hmac.compare_digest(value, secret):
            return True
    return False


class BWDKWebhookAPIView(APIView):
    """POST /bwdk/v1/webhook/ - Digikala notifies us about an order.

    The request must carry the shared Webhook Secret. The body is still NOT trusted: we only pick an
    id out of it and let Get Order decide (same path as the callback page), so it is idempotent.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "bwdk-complete"

    def post(self, request):
        if not _webhook_signature_ok(request):
            log.warning("BWDK webhook rejected: bad or missing secret")
            return Response({"detail": "invalid signature"}, status=403)

        data = request.data if isinstance(request.data, dict) else {}
        bw = None
        mid = data.get("merchant_unique_id")
        if mid:
            bw = BWDKOrder.objects.filter(merchant_unique_id=str(mid)).first()
        if bw is None:
            raw = data.get("order_uuid") or data.get("uuid") or data.get("id")
            try:
                bw = BWDKOrder.objects.filter(order_uuid=UUID(str(raw))).first()
            except (ValueError, TypeError, AttributeError):
                bw = None

        if bw is None:
            log.warning("BWDK webhook: order not found, payload=%s", str(data)[:300])
        else:
            try:
                BWDKService().reconcile(bw.pk)
            except Exception:
                log.exception("BWDK webhook reconcile failed (bwdk #%s)", bw.pk)
        return Response({"ok": True})  # 200 so Digikala does not retry forever
