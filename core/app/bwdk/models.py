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
        related_name="bwdk_order", verbose_name="سفارش داخلی",
    )
    merchant_unique_id = models.CharField(max_length=255, unique=True, verbose_name="شناسه یکتای فروشنده")
    merchant_order_id = models.CharField(max_length=255, db_index=True, verbose_name="شماره سفارش فروشنده")
    order_uuid = models.UUIDField(unique=True, null=True, blank=True, verbose_name="شناسه سفارش در دیجی‌کالا (UUID)")
    order_start_url = models.URLField(max_length=1000, blank=True, verbose_name="لینک شروع پرداخت")
    reference_code = models.CharField(max_length=100, blank=True, verbose_name="کد پیگیری")

    status = models.IntegerField(
        choices=BWDKOrderStatus.choices,
        default=BWDKOrderStatus.PENDING, verbose_name="وضعیت",
    )
    status_display = models.CharField(max_length=100, blank=True, verbose_name="عنوان وضعیت")

    main_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="مبلغ کالاها")
    final_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="مبلغ نهایی")
    total_paid_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="مبلغ پرداخت‌شده")
    discount_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="مبلغ تخفیف")
    promotion_discount_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="تخفیف پروموشن")
    tax_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="مالیات")
    shipping_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="هزینه ارسال")
    packing_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="هزینه بسته‌بندی")
    digipay_markup_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="کارمزد دیجی‌پی")

    payment_data = models.JSONField(default=dict, blank=True, verbose_name="اطلاعات پرداخت")
    destination_address = models.JSONField(default=dict, blank=True, verbose_name="نشانی مقصد")
    shipping_data = models.JSONField(default=dict, blank=True, verbose_name="اطلاعات ارسال")
    customer_data = models.JSONField(default=dict, blank=True, verbose_name="اطلاعات مشتری")
    items_data = models.JSONField(default=list, blank=True, verbose_name="اقلام سفارش")
    last_response = models.JSONField(default=dict, blank=True, verbose_name="آخرین پاسخ دیجی‌کالا")

    # --- lifecycle / safety (added for express checkout) ---
    guest_checkout = models.BooleanField(
        default=False,
        help_text="سفارش بدون ورود به سایت ساخته شده؛ مالک واقعی بعد از پرداخت از روی شماره موبایل پیدا می‌شود.", verbose_name="خرید بدون ورود (مهمان)",
    )
    stock_reserved = models.BooleanField(default=False, verbose_name="موجودی رزرو شده")
    reservation_expires_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="پایان رزرو موجودی")
    verify_attempts = models.PositiveSmallIntegerField(default=0, verbose_name="تعداد تلاش برای Verify")
    last_verify_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان آخرین تلاش Verify")
    finalized_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان نهایی‌شدن")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان لغو")
    needs_review = models.BooleanField(default=False, verbose_name="نیازمند بررسی دستی")
    review_note = models.TextField(blank=True, verbose_name="یادداشت بررسی")

    created_at_bwdk = models.DateTimeField(null=True, blank=True, verbose_name="زمان ایجاد در دیجی‌کالا")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پرداخت")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تایید (Verify)")
    last_synced_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین همگام‌سازی")

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "سفارش خرید با دیجی‌کالا"
        verbose_name_plural = "سفارش‌های خرید با دیجی‌کالا"
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
