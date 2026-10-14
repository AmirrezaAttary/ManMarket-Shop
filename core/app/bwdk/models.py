from django.db import models


class BWDKOrderStatus(models.IntegerChoices):
    PENDING = 3, "PENDING"
    WAITING_FOR_GATEWAY = 4, "WAITING_FOR_GATEWAY"
    EXPIRED = 5, "EXPIRED"
    PAID_BY_USER = 7, "PAID_BY_USER"
    FAILED_TO_PAY = 8, "FAILED_TO_PAY"
    VERIFIED_BY_MERCHANT = 9, "VERIFIED_BY_MERCHANT"
    REFUND_COMPLETED = 17, "REFUND_COMPLETED"
    RESERVATION_EXPIRED = 18, "RESERVATION_EXPIRED"
    DELIVERED = 19, "DELIVERED"
    SHIPPED = 20, "SHIPPED"


class BWDKOrder(models.Model):
    """Local record of an order created in Digikala BWDK."""

    order = models.OneToOneField(
        "order.OrderModel",
        on_delete=models.CASCADE,
        related_name="bwdk_order",
    )
    merchant_unique_id = models.CharField(max_length=255, unique=True)
    merchant_order_id = models.CharField(max_length=255, db_index=True)
    order_uuid = models.UUIDField(unique=True, null=True, blank=True)
    order_start_url = models.URLField(max_length=1000, blank=True)
    reference_code = models.CharField(max_length=100, blank=True)

    status = models.IntegerField(
        choices=BWDKOrderStatus.choices,
        default=BWDKOrderStatus.PENDING,
    )
    status_display = models.CharField(max_length=100, blank=True)

    main_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    final_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    total_paid_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    promotion_discount_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    shipping_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    packing_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    digipay_markup_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)

    payment_data = models.JSONField(default=dict, blank=True)
    destination_address = models.JSONField(default=dict, blank=True)
    shipping_data = models.JSONField(default=dict, blank=True)
    customer_data = models.JSONField(default=dict, blank=True)
    items_data = models.JSONField(default=list, blank=True)
    last_response = models.JSONField(default=dict, blank=True)

    # --- lifecycle / safety (added for express checkout) ---
    guest_checkout = models.BooleanField(
        default=False,
        help_text="سفارش بدون ورود به سایت ساخته شده؛ مالک واقعی بعد از پرداخت از روی شماره موبایل پیدا می‌شود.",
    )
    stock_reserved = models.BooleanField(default=False)
    reservation_expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    verify_attempts = models.PositiveSmallIntegerField(default=0)
    last_verify_attempt_at = models.DateTimeField(null=True, blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    needs_review = models.BooleanField(default=False)
    review_note = models.TextField(blank=True)

    created_at_bwdk = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"BWDK {self.merchant_order_id}"

    @property
    def is_open(self):
        return self.finalized_at is None and self.cancelled_at is None

    @property
    def gateway_name(self):
        return (self.payment_data or {}).get("gateway_name", "")

    @property
    def can_refund(self):
        return (
            self.gateway_name == "Digipay"
            and self.finalized_at is not None
            and self.status != BWDKOrderStatus.REFUND_COMPLETED
        )

    @property
    def can_verify(self):
        return self.is_open and self.status == BWDKOrderStatus.PAID_BY_USER
