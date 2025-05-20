from django.contrib import admin
from .models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance')  # Supprimé 'created_at' et 'updated_at'
    search_fields = ('user__username', 'user__phone')
