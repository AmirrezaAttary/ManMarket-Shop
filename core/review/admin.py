from django.contrib import admin
from .models import ReviewModel

# Register your models here.

@admin.register(ReviewModel)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "rate","status", "created_date")
    search_fields = ("user__email","product__id","product__title")