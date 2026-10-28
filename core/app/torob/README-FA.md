# API ترب (TorobAPI v3)

`POST https://api.manmarket.ir/torob_api/v3/products`  (با و بدون `/` انتهایی)

## چهار حالت ورودی (دقیقاً یکی؛ بدون مقدار پیش‌فرض، هر چیز دیگری → `400 {"error": "..."}`)
| body | خروجی |
|---|---|
| `{"page": 1, "sort": "date_added_desc"}` | صفحه‌بندی ۱۰۰تایی؛ `sort` می‌تواند `date_updated_desc` هم باشد |
| `{"sort": "product_id_desc"}` / `{"cursor": "123", "sort": "product_id_desc"}` | cursor؛ `next_cursor` را بدون تغییر برگردانید، در آخرین صفحه `null` |
| `{"page_uniques": ["12_34"]}` | همان تنوع‌ها؛ موارد حذف/ناموجود در لیست نمی‌آیند |
| `{"page_urls": ["https://manmarket.ir/product/slug?variant=34"]}` | همان بالا |

## هر «رنگ» یک صفحه‌ی ترب است
- `page_unique` = `{شناسه محصول}_{شناسه رنگ(inventory)}`، `product_group_id` = شناسه محصول
- `page_url` = `https://manmarket.ir/product/{slug}?variant={شناسه رنگ}` — فرانت با همین پارامتر رنگ را از پیش انتخاب می‌کند.
  اگر `variant` نباشد، همان رنگی برمی‌گردد که خود سایت به‌صورت پیش‌فرض نشان می‌دهد (کمترین قیمت لیست).
- فقط محصولات منتشرشده (`publish`) و رنگ‌هایی که قیمت > ۰ دارند؛ رنگ ناموجود با `availability=false` می‌آید.
- `current_price` = قیمت نهایی، `old_price` = قیمت بدون تخفیف (یا `null`)، `spec` = مشخصات فعال + «رنگ»، `guarantee` = `warranty`.
- عکس‌ها: اگر برای آن رنگ عکس ثبت شده باشد همان‌ها، وگرنه عکس اصلی + بقیه.
- تاریخ‌ها ISO 8601 با منطقه‌ی زمانی (`+03:30`).

## امنیت
هدر `X-Torob-Token` (JWT، الگوریتم EdDSA) با کلید عمومی ترب بررسی می‌شود: امضا، `exp` و `aud`.
`aud` باید یکی از `TOROB_ALLOWED_AUDIENCES` باشد (پیش‌فرض `api.manmarket.ir`)؛ به هدر Host اعتماد نمی‌شود تا
توکنِ فروشگاه دیگر با Host جعلی دوباره استفاده نشود. توکن نامعتبر → `401`.

## تنظیمات `.env`
`TOROB_PUBLIC_KEY` · `TOROB_ALLOWED_AUDIENCES` · `TOROB_TOKEN_LEEWAY_SECONDS` (۳۰) · `TOROB_SITE_URL` · `TOROB_MEDIA_BASE_URL`

## تست
`python manage.py test app.torob`  (۱۳ تست)
