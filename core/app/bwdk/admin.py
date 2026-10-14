from django.contrib import admin, messages

from .models import BWDKOrder
from .services import BWDKService


@admin.register(BWDKOrder)
class BWDKOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "merchant_order_id", "order_uuid", "reference_code", "status",
        "guest_checkout", "needs_review", "final_amount", "total_paid_amount", "created_date",
    )
    list_filter = ("status", "needs_review", "guest_checkout", "created_date")
    search_fields = ("merchant_order_id", "order_uuid", "reference_code", "merchant_unique_id")
    readonly_fields = (
        "last_response", "payment_data", "destination_address", "shipping_data",
        "customer_data", "items_data",
    )
    actions = ["manual_verify"]

    @admin.action(description="Verify دستی (Get Order سپس Verify اگر status=7)")
    def manual_verify(self, request, queryset):
        service = BWDKService()
        for bw in queryset:
            bw = service.manual_verify(bw)
            self.message_user(request, f"#{bw.pk}: status={bw.status}", messages.INFO)
