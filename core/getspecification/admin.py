from django.contrib import admin
from getspecification.models import PriceSpecification
# Register your models here.
@admin.register(PriceSpecification)
class PriceSpecificationAdmin(admin.ModelAdmin):
    search_fields = ("product",)
    list_display = ("id","product", "url")