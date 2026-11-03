import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from ....bwdk.client import BWDKError
from ....bwdk.models import BWDKOrder, BWDKOrderStatus
from ....bwdk.services import BWDKService
from ...permissions import HasAdminAccessPermission

PAID_STATUSES = (
    BWDKOrderStatus.VERIFIED_BY_MERCHANT,
    BWDKOrderStatus.SHIPPED,
    BWDKOrderStatus.DELIVERED,
)


def _bool_param(value):
    return {"true": True, "false": False}.get(value)


class AdminBWDKListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    """همه‌ی سفارش‌های «خرید با دیجی‌کالا» (BWDK) با فیلتر و خلاصه‌ی وضعیت."""

    template_name = "dashboard/admin/bwdk/bwdk-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        try:
            return min(max(int(self.request.GET.get("page_size", self.paginate_by)), 5), 100)
        except (TypeError, ValueError):
            return self.paginate_by

    def get_queryset(self):
        qs = BWDKOrder.objects.select_related("order")
        params = self.request.GET
        if q := params.get("q", "").strip():
            cond = Q(merchant_order_id__icontains=q) | Q(reference_code__icontains=q)
            if q.isdigit():
                cond |= Q(order_id=int(q)) | Q(pk=int(q))
            qs = qs.filter(cond)
        if status := params.get("status", ""):
            if status.isdigit():
                qs = qs.filter(status=int(status))
        needs_review = _bool_param(params.get("needs_review", ""))
        if needs_review is not None:
            qs = qs.filter(needs_review=needs_review)
        guest = _bool_param(params.get("guest", ""))
        if guest is not None:
            qs = qs.filter(guest_checkout=guest)
        is_open = _bool_param(params.get("open", ""))
        if is_open is not None:
            qs = qs.filter(finalized_at__isnull=is_open, cancelled_at__isnull=is_open)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        stats = BWDKOrder.objects.aggregate(
            total=Count("id"),
            open=Count("id", filter=Q(finalized_at__isnull=True, cancelled_at__isnull=True)),
            needs_review=Count("id", filter=Q(needs_review=True)),
            completed=Count("id", filter=Q(status__in=PAID_STATUSES)),
            refunded=Count("id", filter=Q(status=BWDKOrderStatus.REFUND_COMPLETED)),
            sales=Sum("total_paid_amount", filter=Q(status__in=PAID_STATUSES)),
        )
        ctx["stats"] = stats
        ctx["total_items"] = self.get_queryset().count()
        ctx["status_choices"] = BWDKOrderStatus.choices
        ctx["f"] = {k: self.request.GET.get(k, "") for k in ("q", "status", "needs_review", "guest", "open", "page_size")}
        return ctx


class AdminBWDKDetailView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/bwdk/bwdk-detail.html"
    context_object_name = "bw"

    def get_queryset(self):
        return BWDKOrder.objects.select_related("order", "order__user")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bw = self.object
        ctx["items"] = bw.items_data if isinstance(bw.items_data, list) else []
        ctx["last_response_json"] = json.dumps(bw.last_response or {}, ensure_ascii=False, indent=2)
        return ctx


class _BWDKActionView(LoginRequiredMixin, HasAdminAccessPermission, View):
    http_method_names = ["post"]

    def back(self, bw):
        return redirect("dashboard:admin:bwdk-detail", pk=bw.pk)


class AdminBWDKVerifyView(_BWDKActionView):
    """Get Order و سپس Verify (فقط اگر وضعیت دیجی‌کالا ۷ = پرداخت‌شده باشد)."""

    def post(self, request, pk):
        bw = get_object_or_404(BWDKOrder, pk=pk)
        try:
            bw = BWDKService().manual_verify(bw)
        except Exception as exc:  # خطای شبکه / تنظیمات نباید پنل را از کار بیندازد
            messages.error(request, f"بررسی وضعیت انجام نشد: {exc}")
            return self.back(bw)
        if bw.finalized_at:
            messages.success(request, "سفارش دیجی‌کالا تأیید (Verify) و نهایی شد ✅")
        else:
            messages.warning(request, f"سفارش هنوز قابل تأیید نیست. وضعیت دیجی‌کالا: {bw.status_display or bw.status}")
        return self.back(bw)


class AdminBWDKRefundView(_BWDKActionView):
    """بازگشت وجه کامل (فقط پرداخت‌های دیجی‌پی)."""

    def post(self, request, pk):
        bw = get_object_or_404(BWDKOrder, pk=pk)
        reason = (request.POST.get("reason") or "انصراف مشتری از خرید").strip()[:255]
        try:
            BWDKService().refund(bw, reason)
            messages.success(request, "درخواست بازگشت وجه ثبت شد ✅")
        except (ValueError, BWDKError) as exc:
            messages.error(request, f"بازگشت وجه انجام نشد: {exc}")
        return self.back(bw)


class AdminBWDKReviewDoneView(_BWDKActionView):
    """بعد از بررسی دستی، پرچم «نیازمند بررسی» را برمی‌دارد."""

    def post(self, request, pk):
        bw = get_object_or_404(BWDKOrder, pk=pk)
        bw.needs_review = False
        bw.save(update_fields=["needs_review", "updated_date"])
        messages.success(request, "سفارش به‌عنوان «بررسی‌شده» علامت خورد.")
        return self.back(bw)


class AdminBWDKSyncAllView(LoginRequiredMixin, HasAdminAccessPermission, View):
    """همان کاری که bwdk_sync با cron می‌کند: Verify مجدد و آزادسازی رزروهای منقضی."""

    http_method_names = ["post"]

    def post(self, request):
        try:
            done = BWDKService().sync_open_orders()
            messages.success(request, f"همگام‌سازی انجام شد؛ {done} سفارش بررسی شد.")
        except Exception as exc:
            messages.error(request, f"همگام‌سازی انجام نشد: {exc}")
        return redirect(request.POST.get("next") or reverse("dashboard:admin:bwdk-list"))
