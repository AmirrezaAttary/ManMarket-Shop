from django.contrib import admin
from ..website.models import Contact, AboutGrop, Story, SiteSetting, Banner, FAQ


# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = ('name','email','created_date')
    list_filter = ('email',)
    search_fields = ('name','message')
    
    
@admin.register(AboutGrop)
class AboutGropAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = ('name','job','created_date')
    list_filter = ('name',)
    search_fields = ('name','job')

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('title', 'user', 'status', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('id','title', 'user__email')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    """تنظیمات سایت فقط یک رکورد دارد؛ نه اضافه می‌شود و نه حذف."""
    fieldsets = (
        ("اطلاعات فروشگاه", {"fields": ("site_name", "logo", "favicon")}),
        ("اطلاعات تماس", {"fields": ("phone", "support_phone", "email", "address", "working_hours")}),
        ("شبکه‌های اجتماعی", {"fields": ("instagram", "telegram", "whatsapp", "eitaa")}),
        ("نوار اعلان بالای سایت", {"fields": ("announcement_active", "announcement_text", "announcement_link")}),
        ("ارسال و فوتر", {"fields": ("free_shipping_threshold", "footer_text", "enamad_code")}),
        ("سئو", {"fields": ("meta_title", "meta_description")}),
    )

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "position", "sort_order", "is_active", "start_date", "end_date")
    list_filter = ("position", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "link")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "sort_order", "is_active")
    list_filter = ("category", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("question", "answer")
