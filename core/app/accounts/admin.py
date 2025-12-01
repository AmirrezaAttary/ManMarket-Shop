from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile,OTP
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.timezone import now

# Register your models here.

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for user management based on phone_number
    """
    model = User

    # ستون‌ها در لیست کاربران
    list_display = (
        "id",
        "phone_number",
        "is_superuser",
        "is_active",
        "is_verified",
        
    )

    # فیلترها
    list_filter = (
        "is_superuser",
        "is_active",
        "is_verified",
        
    )

    search_fields = ("phone_number",)
    ordering = ("-id",)

    # فیلدهای فقط خواندنی
    readonly_fields = ("last_login", "created_date", "updated_date")

    # فرم تغییر کاربر
    fieldsets = (
        (
            "Authentication",
            {
                "fields": ("phone_number", "password", "email", "code_melli"),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    
                ),
            },
        ),
        (
            "Group Permissions",
            {
                "fields": ("groups", "user_permissions", "type"),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login", "created_date", "updated_date"),
            },
        ),
    )

    # فرم افزودن کاربر
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "type",
                ),
            },
        ),
    )



class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ("id","user", "first_name","last_name")
    searching_fields = ("user","first_name","last_name")


admin.site.register(Profile,CustomProfileAdmin)
# admin.site.register(User, CustomUserAdmin)

from django.contrib.sessions.models import Session
class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']
admin.site.register(Session, SessionAdmin)




# accounts/admin.py





@admin.register(OTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used', 'valid_status')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__phone_number', 'code')
    ordering = ('-created_at',)

    def valid_status(self, obj):
        """نمایش وضعیت معتبر بودن OTP"""
        if obj.is_valid():
            return format_html('<span style="color: green;">✅ معتبر</span>')
        else:
            return format_html('<span style="color: red;">❌ منقضی</span>')
    valid_status.short_description = 'وضعیت اعتبار'

    def get_queryset(self, request):
        """لود پیشرفته با select_related برای کاربر"""
        return super().get_queryset(request).select_related('user')

    readonly_fields = ('user', 'code', 'created_at', 'is_used')

    fieldsets = (
        (None, {
            'fields': ('user', 'code', 'is_used', 'created_at')
        }),
    )
