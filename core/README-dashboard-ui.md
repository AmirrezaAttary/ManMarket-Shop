# طراحی جدید پنل مدیریت (Tailwind)

## نصب
فایل‌های این بسته را روی پروژه‌ی خودتان کپی کنید (پوشه‌ها با ساختار اصلی یکسان‌اند):
- templates/        → همه‌ی صفحات پنل، login.html، 404.html و messages.html
- staticfiles/css/dashboard.css → CSS ساخته‌شده‌ی تیلویند (آماده‌ی استفاده، نیازی به Node نیست)
- tailwind/, package.json → فقط برای زمانی که بخواهید استایل را تغییر دهید

بعد از کپی: `python manage.py collectstatic` (اگر لازم است).

## تغییر دادن استایل (اختیاری)
    npm install
    npm run build:css      # ساخت دوباره‌ی dashboard.css
    npm run watch:css      # در زمان توسعه

رنگ نارنجی برند در tailwind/tailwind.config.js (brand-500 = #f96747) تعریف شده است.

## نکته‌ها
- پنل دیگر هیچ فایل Bootstrap/style.css/admin-panel.css را لود نمی‌کند (فقط dashboard.css).
- در موبایل جدول‌ها خودکار به کارت تبدیل می‌شوند و منو به‌صورت کشویی باز می‌شود.
- دکمه‌ها ۴۴px، دکمه‌های کوچک ۳۶px و همه‌ی فیلدها ۴۴px ارتفاع دارند.
- آیکن‌ها از یک sprite داخلی (dashboard/admin/_sprite.html) می‌آیند و دیگر به bootstrap-icons نیاز نیست.
