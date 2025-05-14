from django.contrib import admin
from website.models import Contact,AboutGrop


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
