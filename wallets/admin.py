from django.contrib import admin
from .models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'created_at', 'updated_at')  # Ajoute ici les champs existants
    search_fields = ('user__username', 'user__phone')
    list_filter = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
