from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    subject = models.CharField(max_length=255,null=True, blank=True, verbose_name="موضوع")
    message = models.TextField(verbose_name="پیام")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "پیام تماس با ما"
        verbose_name_plural = "پیام‌های تماس با ما"
        ordering = ['-created_date']
    def __str__(self):
        return self.name
    
    
class AboutGrop(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام")
    image = models.ImageField(upload_to='about/',default='about/default.png', verbose_name="عکس")
    job = models.CharField(max_length=255, verbose_name="سمت")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "عضو تیم"
        verbose_name_plural = "اعضای تیم (درباره ما)"
        ordering = ['-created_date']
    def __str__(self):
        return self.name
    
    
    
class ReviewStatusType(models.IntegerChoices):
    pending = 1, "در انتظار تایید"
    accepted = 2, "تایید شده"
    rejected = 3, "رد شده"


User = get_user_model()

class Story(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories', verbose_name="کاربر")
    title = models.CharField(max_length=255, verbose_name='تایتل')
    video = models.FileField(upload_to='stories/videos/', verbose_name='فیلم')
    icon = models.ImageField(upload_to='stories/icons/', verbose_name='آیکون استوری')
    status = models.IntegerField(
            choices=ReviewStatusType.choices, default=ReviewStatusType.pending.value, verbose_name='آیکون استوری')
    product = models.ForeignKey('shop.ProductModel', on_delete=models.CASCADE,null=True,blank=True, verbose_name="محصول")
    title_product = models.CharField(max_length=255,default="لینک محصول", verbose_name="عنوان لینک محصول")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "استوری"
        verbose_name_plural = "استوری‌ها"

    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def get_status(self):
        return {
            "id":self.status,
            "title":ReviewStatusType(self.status).name,
            "label":ReviewStatusType(self.status).label,
        }


# ---------------------------------------------------------------------------
# مدل‌های مورد نیاز فروشگاه (تنظیمات سایت، بنر، منو، سوالات متداول، ...)
# ---------------------------------------------------------------------------
class SiteSetting(models.Model):
    """تنظیمات کلی سایت (فقط یک رکورد دارد)."""

    site_name = models.CharField("نام فروشگاه", max_length=120, default="من مارکت")
    logo = models.ImageField("لوگو", upload_to="site/", null=True, blank=True)
    favicon = models.ImageField("فاوآیکون", upload_to="site/", null=True, blank=True)

    phone = models.CharField("تلفن تماس", max_length=30, blank=True)
    support_phone = models.CharField("شماره پشتیبانی / واتساپ", max_length=30, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    address = models.CharField("نشانی", max_length=500, blank=True)
    working_hours = models.CharField("ساعات کاری", max_length=200, blank=True)

    instagram = models.URLField("اینستاگرام", blank=True)
    telegram = models.URLField("تلگرام", blank=True)
    whatsapp = models.URLField("واتساپ", blank=True)
    eitaa = models.URLField("ایتا", blank=True)

    announcement_active = models.BooleanField("نمایش نوار اعلان بالای سایت", default=False)
    announcement_text = models.CharField("متن نوار اعلان", max_length=255, blank=True)
    announcement_link = models.URLField("لینک نوار اعلان", blank=True)

    free_shipping_threshold = models.PositiveIntegerField(
        "حداقل خرید برای ارسال رایگان (تومان)", null=True, blank=True,
        help_text="خالی = ارسال رایگان نداریم",
    )
    footer_text = models.TextField("متن پایین سایت (فوتر)", blank=True)
    enamad_code = models.TextField(
        "کد نماد اعتماد (اینماد / ساماندهی)", blank=True,
        help_text="کد HTML که از سایت اینماد می‌گیرید.",
    )
    meta_title = models.CharField("عنوان سئو (Title)", max_length=255, blank=True)
    meta_description = models.CharField("توضیحات سئو (Description)", max_length=300, blank=True)

    updated_date = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # تنظیمات حذف نمی‌شود
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BannerPosition(models.IntegerChoices):
    hero = 1, "اسلایدر اصلی صفحه‌ی اول"
    promo = 2, "بنر زیر اسلایدر"
    sidebar = 3, "بنر کناری"
    popup = 4, "پاپ‌آپ"
    category = 5, "بنر صفحه‌ی دسته‌بندی"


class Banner(models.Model):
    title = models.CharField("عنوان", max_length=200)
    image = models.ImageField("تصویر دسکتاپ", upload_to="banners/")
    mobile_image = models.ImageField("تصویر موبایل", upload_to="banners/mobile/", null=True, blank=True)
    link = models.CharField("لینک", max_length=500, blank=True, help_text="می‌تواند آدرس کامل یا مسیر داخلی سایت باشد.")
    alt_text = models.CharField("متن جایگزین تصویر", max_length=200, blank=True)
    position = models.IntegerField("جایگاه", choices=BannerPosition.choices, default=BannerPosition.hero.value)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    is_active = models.BooleanField("فعال", default=True)
    start_date = models.DateTimeField("شروع نمایش", null=True, blank=True)
    end_date = models.DateTimeField("پایان نمایش", null=True, blank=True)
    created_date = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_date = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        ordering = ["position", "sort_order", "-created_date"]
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"

    def __str__(self):
        return self.title


class FAQCategory(models.IntegerChoices):
    # نام‌ها (login_register, ...) با شناسه‌ی تب‌های صفحه‌ی سوالات متداول فرانت یکی است
    login_register = 1, "ورود و ثبت نام"
    shipping = 2, "شیوه‌ها و هزینه ارسال"
    order_process = 3, "فرایند ثبت سفارش"
    order_tracking = 4, "پیگیری سفارش"
    returns = 5, "ضمانت برگشت و گارانتی"
    general_faqs = 6, "سوالات عمومی"
    other = 7, "سایر موارد"


class FAQ(models.Model):
    question = models.CharField("پرسش", max_length=300)
    answer = models.TextField("پاسخ")
    category = models.IntegerField("دسته‌بندی", choices=FAQCategory.choices, default=FAQCategory.general_faqs.value)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    is_active = models.BooleanField("فعال", default=True)
    created_date = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_date = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        ordering = ["category", "sort_order", "id"]
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"

    def __str__(self):
        return self.question
