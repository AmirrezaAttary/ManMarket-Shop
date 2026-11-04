from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from .coupon_logic import compute_discount
from ..accounts.validators import validate_iranian_cellphone_number

class TrackingType(models.IntegerChoices):
    post = 1 , "ارسال با پست عادی"
    mahex = 2 , "ارسال با ماهکس"
    tipax = 3 , "ارسال با تیپاکس"
    person = 4, "حضوری"
    

class OrderStatusType(models.IntegerChoices):
    pending = 1 , "در انتظار پرداخت"
    awaiting = 2, "در انتظار تایید سفارش"
    success = 3, "در حال پردازش"
    shipped = 4, "ارسال شده"
    deliverd = 5, "تحویل شده"
    failed = 6,"لغو شده"


class UserAddressModel(models.Model):
    user = models.ForeignKey('accounts.User',on_delete=models.CASCADE, verbose_name="کاربر")
    name = models.CharField(max_length=250,default="", verbose_name="نام گیرنده")
    phone_number = models.CharField(max_length=12,default="",validators=[validate_iranian_cellphone_number], verbose_name="شماره تماس")
    
    address = models.CharField(max_length=250, verbose_name="نشانی")
    state = models.CharField(max_length=50, verbose_name="استان")
    city = models.CharField(max_length=50, verbose_name="شهر")
    zip_code = models.CharField(max_length=50, verbose_name="کد پستی")

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "نشانی کاربر"
        verbose_name_plural = "نشانی‌های کاربران"

class CouponType(models.TextChoices):
    percent = "percent", "درصدی"
    percent_capped = "percent_capped", "درصدی با سقف"
    fixed = "fixed", "مبلغ ثابت"


class CouponModel(models.Model):
    code = models.CharField(max_length=100, verbose_name="کد تخفیف")
    discount_type = models.CharField(max_length=20, choices=CouponType.choices, default=CouponType.percent.value, verbose_name="نوع تخفیف")
    discount_percent = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="درصد تخفیف")
    max_discount_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name="سقف تخفیف (تومان)")
    discount_amount = models.PositiveIntegerField(default=0, blank=True, verbose_name="مبلغ تخفیف ثابت (تومان)")
    min_order_amount = models.PositiveIntegerField(default=0, blank=True, verbose_name="حداقل مبلغ سفارش (تومان)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    max_limit_usage = models.PositiveIntegerField(default=10, verbose_name="حداکثر دفعات استفاده")
    per_user_limit = models.PositiveIntegerField(default=1, verbose_name="حداکثر استفاده‌ی هر کاربر (۰ = نامحدود)")
    used_by = models.ManyToManyField('accounts.User',related_name = "coupon_users",blank=True, verbose_name="استفاده‌شده توسط")

    expiration_date = models.DateTimeField(null=True,blank=True, verbose_name="تاریخ انقضا")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

    # ---------- وضعیت ----------
    @property
    def used_count(self):
        """تعداد سفارش‌هایی که با این کد ثبت شده‌اند (سفارش‌های لغو/ناموفق حساب نمی‌شوند)."""
        return self.ordermodel_set.exclude(status=OrderStatusType.failed.value).count()

    @property
    def is_expired(self):
        return bool(self.expiration_date and self.expiration_date < timezone.now())

    def get_summary(self):
        """متن کوتاه برای نمایش در لیست‌ها."""
        if self.discount_type == CouponType.fixed.value:
            return f"{self.discount_amount:,} تومان"
        if self.discount_type == CouponType.percent_capped.value and self.max_discount_amount:
            return f"{self.discount_percent}٪ تا سقف {self.max_discount_amount:,} تومان"
        return f"{self.discount_percent}٪"

    # ---------- محاسبه و اعتبارسنجی ----------
    def calculate_discount(self, subtotal):
        return compute_discount(
            self.discount_type,
            subtotal,
            percent=self.discount_percent,
            max_discount=self.max_discount_amount,
            fixed=self.discount_amount,
        )

    def get_discount_for(self, user, subtotal):
        """
        مبلغ تخفیف را برای این کاربر و جمع سفارش برمی‌گرداند.
        اگر کد قابل استفاده نباشد، ValidationError با پیام فارسی می‌دهد.
        """
        if not self.is_active:
            raise ValidationError("این کد تخفیف غیرفعال است.")
        if self.is_expired:
            raise ValidationError("مهلت استفاده از این کد تخفیف به پایان رسیده است.")
        if self.min_order_amount and int(subtotal) < self.min_order_amount:
            raise ValidationError(f"این کد برای سفارش‌های بالای {self.min_order_amount:,} تومان قابل استفاده است.")

        used = self.ordermodel_set.exclude(status=OrderStatusType.failed.value)
        if self.max_limit_usage and used.count() >= self.max_limit_usage:
            raise ValidationError("ظرفیت استفاده از این کد تخفیف تکمیل شده است.")
        if self.per_user_limit and used.filter(user=user).count() >= self.per_user_limit:
            raise ValidationError("شما قبلاً از این کد تخفیف استفاده کرده‌اید.")

        discount = self.calculate_discount(subtotal)
        if discount <= 0:
            raise ValidationError("این کد تخفیف روی این سفارش اعمال نمی‌شود.")
        return discount


# Create your models here.
class OrderModel(models.Model):
    user = models.ForeignKey('accounts.User',on_delete=models.CASCADE,related_name='order_user', verbose_name="کاربر")
    name = models.CharField(max_length=250,default="", verbose_name="نام گیرنده")
    phone_number = models.CharField(max_length=250,default="", verbose_name="شماره تماس")

    # order address information
    address = models.CharField(max_length=250, verbose_name="نشانی")
    state = models.CharField(max_length=50, verbose_name="استان")
    city = models.CharField(max_length=50, verbose_name="شهر")
    zip_code = models.CharField(max_length=50, verbose_name="کد پستی")
    
    payment = models.ForeignKey('payment.PaymentModel',on_delete=models.SET_NULL,null=True,blank=True, verbose_name="پرداخت")
    
    
    total_price = models.DecimalField(default=0,max_digits=10,decimal_places=0, verbose_name="مبلغ کل (تومان)")
    coupon = models.ForeignKey(CouponModel,on_delete=models.PROTECT,null=True,blank=True, verbose_name="کد تخفیف")
    status = models.IntegerField(choices=OrderStatusType.choices,default=OrderStatusType.pending.value, verbose_name="وضعیت سفارش")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    tracking_type = models.IntegerField(choices=TrackingType.choices,default=TrackingType.post.value, verbose_name="نوع ارسال")
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد رهگیری پستی")
    
    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_date']
    
    def calculate_total_price(self):
        return sum(item.price * item.quantity for item in self.order_items.all())
    
    def __str__(self):
        user_email = getattr(self.user, "email", None) or "کاربر نامشخص"
        return f"{user_email} - {self.id}"
    
    def get_status(self):
        return {
            "id":self.status,
            "title":OrderStatusType(self.status).name,
            "label":OrderStatusType(self.status).label,
        }
        
    def get_full_address(self):
        return f"{self.state},{self.city},{self.address}"
    
    @property
    def order_number(self):
        """شماره سفارش به صورت تاریخ + ID"""
        return f"{self.created_date.strftime('%Y%m%d')}{self.id}"
    
    @property
    def is_successful(self):
        return self.status == OrderStatusType.success.value
    
    def get_price(self):
        # total_price هنگام ثبت سفارش، بعد از کسر تخفیف ذخیره می‌شود
        return self.total_price

    def get_discount_amount(self):
        """مبلغ تخفیف اعمال‌شده (از روی جمع آیتم‌ها و مبلغ نهایی؛ برای سفارش‌های قدیمی هم درست است)."""
        if not self.coupon_id:
            return 0
        return max(int(self.calculate_total_price() - self.total_price), 0)

    def get_price_before_discount(self):
        return self.total_price + self.get_discount_amount()

    def get_tracking_url(self):
        if self.tracking_code:
            return f"https://mahex.com/tracking?consignmentId={self.tracking_code}"
        return None
    
    
class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel,on_delete=models.CASCADE,related_name="order_items", verbose_name="سفارش") 
    product = models.ForeignKey('shop.ProductModel',on_delete=models.PROTECT, verbose_name="محصول")
    color = models.ForeignKey('shop.Color',on_delete=models.PROTECT, verbose_name="رنگ")
    quantity = models.PositiveIntegerField(default=0, verbose_name="تعداد")
    price = models.DecimalField(default=0,max_digits=10,decimal_places=0, verbose_name="قیمت واحد")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    def __str__(self):
        return f"{self.product.title} - {self.order.id}"

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"
    