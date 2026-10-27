# فید کاتالوگ دیجیفای (روش ۱: خواندن دوره‌ای)

پیاده‌سازی بخش «خواندن دوره‌ای (Periodic Crawl)» مستند اتصال API فروشندگان برای من‌مارکت.

## آدرس‌ها (به تیم فنی بازار بدهید)
| مسیر | کاربرد |
|---|---|
| `GET https://api.manmarket.ir/digify/v1/products/?limit=&offset=&updated_after=` | لیست محصولات (PLP) |
| `GET https://api.manmarket.ir/digify/v1/products/{id}/` | جزئیات محصول + تنوع‌ها (PDP) |

- `updated_after`: timestamp یونیکس (ثانیه، UTC) و اختیاری. `total` همیشه تعداد نتایج همان فیلتر است.
- ترتیب: بدون `updated_after` → `created_date, id` صعودی؛ با `updated_after` → `updated_at, created_date, id` صعودی.
- `limit` پیش‌فرض ۱۰۰ و حداکثر ۲۰۰ (قابل تنظیم). پارامتر نامعتبر → `400`.

## نگاشت مدل‌ها
- محصول → `ProductModel`؛ هر **رنگ** (`ProductColorInventory`) → یک **variant** با ویژگی «رنگ» (`is_color` + `color_code`).
- `price` = قیمت نهایی (بعد از تخفیف)، `original_price` = قیمت قبل از تخفیف (فقط اگر تخفیف باشد، وگرنه `null`).
- سطح محصول: قیمت ارزان‌ترین تنوع **موجود**؛ اگر هیچ تنوعی موجود نباشد `is_available=false`.
- محصول پیش‌نویس (`draft`) حذف نمی‌شود؛ با `is_available=false` و `stock=0` گزارش می‌شود تا در بازار ناموجود شود.
- محصول بدون تنوع → یک variant جایگزین با `is_available=false` (طبق سند آرایه‌ی `variants` نباید خالی باشد).
- `category_path` = `[عنوان دسته]` (مدل فقط یک سطح دسته دارد؛ بدون دسته → «سایر»).
- `preparation_time_in_days` از `BWDK_DEFAULT_PREPARATION_TIME` می‌آید (همان مقدار سفارش‌های BWDK).

## `updated_at` چطور دقیق می‌ماند
`updated_at` = جدیدترین زمان بین ردیف محصول و ردیف‌های موجودی/قیمت آن. برای اینکه تغییرات مخفی نمانند:
- `ProductColorInventory.objects.update(...)` (رزرو/برگشت موجودی BWDK، اسکریپت‌های pricegethamrh) حالا خودش `updated_date` را هم به‌روز می‌کند (`InventoryQuerySet` در `shop/models/colors.py`).
- حذف یک رنگ، تغییر عکس‌های محصول، تغییر برند/دسته/رنگ → سیگنال‌های `digify/signals.py`.

## تنظیمات (`.env`)
| متغیر | پیش‌فرض | توضیح |
|---|---|---|
| `DIGIFY_FEED_API_KEY` | خالی | خالی = فید عمومی. اگر مقدار بدهید باید `Authorization: Api-Key <key>` یا `X-Api-Key` ارسال شود |
| `DIGIFY_FEED_ALLOWED_IPS` | خالی | لیست IP مجاز، با کاما جدا شود |
| `DIGIFY_SITE_URL` | `https://manmarket.ir` | برای `source_url` (`/product/{slug}`) |
| `DIGIFY_MEDIA_BASE_URL` | `https://api.manmarket.ir` | مبدأ عمومی `/media/` برای URL تصاویر |
| `DIGIFY_FEED_DEFAULT_LIMIT` / `DIGIFY_FEED_MAX_LIMIT` | `100` / `200` | |

## تست
`python manage.py test app.digify`  (۱۲ تست)
