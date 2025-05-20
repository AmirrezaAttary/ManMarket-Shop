# views.py
from django.http import FileResponse
from django.contrib.admin.views.decorators import staff_member_required
import os
from django.http import HttpResponse
from django.conf import settings
from django.views import View
from dashboard.permissions import HasAdminAccessPermission
from io import BytesIO
import zipfile

 # فقط کاربر ادمین اجازه دارد


class DownloadDatabaseView(HasAdminAccessPermission, View):
    def test_func(self):
        # اینجا لاجیک permission خودت رو می‌نویسی.
        # مثلا کاربر باید superuser یا نوع خاصی باشه
        return self.request.user.is_authenticated and self.request.user.is_superuser
        # یا مثلا:
        # return self.request.user.is_news_admin

    def get(self, request, *args, **kwargs):
        db_path = os.path.join(settings.BASE_DIR,  'db.sqlite3')
        if os.path.exists(db_path):
            return FileResponse(open(db_path, 'rb'), as_attachment=True, filename='backup.sqlite3')
        return HttpResponse("فایل دیتابیس پیدا نشد.", status=404)
    
    
class DownloadMediaView(HasAdminAccessPermission, View):
    def test_func(self):
        # اجازه دسترسی
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        media_path = os.path.join(settings.BASE_DIR, 'media')
        if not os.path.exists(media_path):
            return HttpResponse("پوشه media پیدا نشد.", status=404)

        # ایجاد یک فایل ZIP در حافظه
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(media_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # مسیر فایل درون ZIP رو طوری تنظیم می‌کنیم که پوشه media حذف بشه
                    relative_path = os.path.relpath(file_path, media_path)
                    zip_file.write(file_path, arcname=relative_path)

        zip_buffer.seek(0)

        # ارسال فایل ZIP به عنوان پاسخ دانلود
        response = FileResponse(zip_buffer, as_attachment=True, filename="media_backup.zip")
        return response