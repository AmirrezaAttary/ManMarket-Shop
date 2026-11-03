from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ....blog.models import BlogStatusType, Category, Post
from ...models import Banner, BannerPosition

CAMPAIGN_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "campaign"

# دکمه‌ی بنرها به صفحه‌ی محصولات می‌رود (از پنل ادمین → بنرها قابل تغییر است)
PRODUCTS_URL = "/category/phone"

BANNERS = [
    {
        "title": "خرید با دیجی‌کالا؛ مثل دیجی‌کالا سفارش بده",
        "file": "bwdk-banner-general.webp",
        "alt": "خرید با دیجی‌کالا: ورود سریع، پرداخت اقساطی، ارسال دیجی‌کالایی",
        "sort_order": 1,
    },
    {
        "title": "خرید اقساطی با دیجی‌پی؛ الان بخر، بعدا پرداخت کن",
        "file": "bwdk-banner-digipay.webp",
        "alt": "خرید اقساطی با دیجی‌پی در من مارکت",
        "sort_order": 2,
    },
]

POST_TITLE = "راهنمای خرید با دیجی‌کالا در من مارکت"
POST_META = (
    "خرید اینترنتی از من مارکت وقتی لذت‌بخش می‌شود که سریع، مطمئن و بدون دردسر باشد. "
    "با «خرید با دیجی‌کالا» با حساب دیجی‌کالای خود سفارش بدهید، نقدی یا اقساطی با دیجی‌پی پرداخت کنید."
)

IMG_STYLE = "width:100%;height:auto;border-radius:12px;margin:12px 0;"


def post_content(urls):
    img = lambda key, alt: f'<p><img src="{urls[key]}" alt="{alt}" style="{IMG_STYLE}"></p>'
    return f"""
<p>خرید اینترنتی از «من مارکت» وقتی لذت‌بخش می‌شود که سریع، مطمئن و بدون دردسر باشد. برای همین، قابلیت پرداخت و ثبت سفارش سریع را با سرویس <strong>«خرید با دیجی‌کالا»</strong> فعال کرده‌ایم؛ بخشی از تجربه‌ای که میلیون‌ها کاربر در دیجی‌کالا می‌شناسند، حالا روی سایت ما هم در دسترس است.</p>

<h2>«خرید با دیجی‌کالا» یعنی چه؟</h2>
<p>یعنی می‌توانید بدون ساختن حساب جدید و فقط با حساب دیجی‌کالای خودتان سفارش بدهید:</p>
<ul>
<li>با حساب دیجی‌کالا وارد می‌شوید.</li>
<li>نقدی، یا اعتباری و اقساطی با دیجی‌پی پرداخت می‌کنید.</li>
<li>سفارش را دیجی‌کالایی تحویل می‌گیرید.</li>
</ul>
{img("guide-1", "دکمه خرید با دیجی‌کالا؛ امن، سریع و قسطی")}

<h2>مرحله اول: انتخاب محصول و زدن دکمه</h2>
<p>محصول مورد نظرتان را انتخاب کنید و در صفحه محصول یا در سبد خرید، دکمه <strong>«خرید با دیجی‌کالا»</strong> را بزنید. اگر محصول امکان پرداخت اقساطی داشته باشد، گزینه‌ی اقساطی را هم همین‌جا می‌بینید.</p>
{img("guide-2", "دکمه خرید با دیجی‌کالا در سبد خرید")}

<h2>مرحله دوم: ورود با حساب دیجی‌کالا</h2>
<p>شماره موبایل یا ایمیل حساب دیجی‌کالای خود را وارد کنید و تأیید کنید. اگر هنوز در دیجی‌کالا حساب ندارید، همان‌جا می‌توانید ثبت‌نام کنید.</p>
{img("guide-3", "ورود یا ثبت‌نام در دیجی‌کالا")}

<h2>مرحله سوم: آدرس و زمان تحویل</h2>
<p>آدرس‌های ثبت‌شده در حساب دیجی‌کالای شما نمایش داده می‌شود و آدرس پیش‌فرضتان از قبل انتخاب شده است. قبل از پرداخت می‌توانید آدرس را تغییر دهید یا آدرس جدید اضافه کنید و بازه‌ی زمانی تحویل سفارش را انتخاب کنید.</p>
{img("guide-4", "انتخاب آدرس و زمان تحویل سفارش")}

<h2>مرحله چهارم: پرداخت</h2>
<p>روش پرداخت را انتخاب کنید:</p>
<ul>
<li><strong>پرداخت نقدی:</strong> پرداخت اینترنتی با کارت‌های بانکی.</li>
<li><strong>پرداخت اعتباری دیجی‌پی:</strong> خرید اقساطی با اعتبار دیجی‌پی؛ بدون نیاز به پرداخت کل مبلغ در لحظه‌ی خرید.</li>
</ul>
{img("guide-5", "انتخاب روش پرداخت نقدی یا اعتباری دیجی‌پی")}

<h2>پیگیری سفارش</h2>
<p>بعد از ثبت سفارش، یک <strong>کد پیگیری</strong> که با <strong>BD</strong> شروع می‌شود دریافت می‌کنید. برای پیگیری سفارش یا هر سوال دیگر، همین کد را به پشتیبانی من مارکت اعلام کنید تا سریع‌تر بررسی شود.</p>

<h2>مرجوعی و بازگشت وجه</h2>
<p>اگر نیاز به مرجوع کردن سفارش داشتید، با پشتیبانی من مارکت در ارتباط باشید. نحوه‌ی بازگشت وجه به روش پرداخت سفارش (نقدی یا دیجی‌پی) بستگی دارد و پشتیبانی شما را راهنمایی می‌کند.</p>

<h2>همین حالا امتحان کنید</h2>
<p>محصولات من مارکت را ببینید و در سه کلیک، با «خرید با دیجی‌کالا» سفارش بدهید. از <a href="{PRODUCTS_URL}">صفحه‌ی محصولات</a> شروع کنید.</p>
""".strip()


class Command(BaseCommand):
    help = (
        "کمپین «خرید با دیجی‌کالا»: دو بنر لینک‌دار (جایگاه «بنر زیر اسلایدر») و مقاله‌ی راهنمای وبلاگ را می‌سازد. "
        "چند بار اجرا کردنش امن است؛ موارد موجود دوباره ساخته نمی‌شوند."
    )

    def handle(self, *args, **options):
        created_banners = 0
        for spec in BANNERS:
            if Banner.objects.filter(title=spec["title"]).exists():
                continue
            banner = Banner(
                title=spec["title"],
                link=PRODUCTS_URL,
                alt_text=spec["alt"],
                position=BannerPosition.promo.value,
                sort_order=spec["sort_order"],
                is_active=True,
            )
            banner.image.save(spec["file"], ContentFile((CAMPAIGN_DIR / spec["file"]).read_bytes()), save=False)
            banner.save()
            created_banners += 1

        slug = slugify(POST_TITLE, allow_unicode=True)
        post_created = False
        if not Post.objects.filter(slug=slug).exists():
            urls = {}
            for key in ("guide-1", "guide-2", "guide-3", "guide-4", "guide-5"):
                stored = default_storage.save(f"blog/images/bwdk-{key}.webp", ContentFile((CAMPAIGN_DIR / f"{key}.webp").read_bytes()))
                urls[key] = default_storage.url(stored)
            post = Post(
                title=POST_TITLE,
                slug=slug,
                content=post_content(urls),
                meta_description=POST_META[:255],
                status=BlogStatusType.publish.value,
            )
            post.image.save("bwdk-guide-cover.webp", ContentFile((CAMPAIGN_DIR / "guide-cover.webp").read_bytes()), save=False)
            post.save()
            category, _ = Category.objects.get_or_create(name="راهنمای خرید", defaults={"slug": slugify("راهنمای خرید", allow_unicode=True)})
            post.category.add(category)
            post.tags.add("خرید با دیجی‌کالا", "راهنمای خرید", "دیجی‌پی")
            post_created = True

        self.stdout.write(self.style.SUCCESS(
            f"{created_banners} بنر ساخته شد؛ مقاله‌ی راهنما: {'ساخته شد' if post_created else 'از قبل بود'}"
        ))
