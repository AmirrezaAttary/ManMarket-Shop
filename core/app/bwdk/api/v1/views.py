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
