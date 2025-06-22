from django.contrib import admin
from .models import Wallet, WalletTransaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'balance')
    search_fields = ('user__email',)
@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('id','wallet', 'amount', 'created_at', 'transaction_type', 'description')
    list_filter = ('transaction_type',)
    search_fields = ('wallet__user__email', 'description')
# Register your models here.
