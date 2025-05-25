# wallets/admin.py
from django.contrib import admin
from .models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'currency', 'created_at', 'updated_at') # Ajout de 'currency'
    search_fields = ('user__username', 'user__phone')
    list_filter = ('currency', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
