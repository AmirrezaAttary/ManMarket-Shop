from django.contrib import admin
from ..pricegethamrh.models import PriceGetHamrh
# Register your models here.
@admin.register(PriceGetHamrh)
class PriceGetHamrhAdmin(admin.ModelAdmin):
    search_fields = ("product__title","product__id","url")
    list_display = ("id","product", "url")