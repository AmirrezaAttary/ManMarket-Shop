from django.contrib import admin
from website.models import Contact,AboutGrop, Story


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