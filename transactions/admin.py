# transactions/admin.py
from django.contrib import admin
from .models import Transaction, DiscountCode

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle Transaction.
    Permet aux administrateurs de voir et gérer les transactions.
    """
    list_display = (
        'sender', 'receiver', 'amount', 'final_amount', 'discount_code_used',
        'status', 'transaction_type', 'created_at'
    )
    list_filter = ('status', 'transaction_type', 'created_at', 'discount_code_used')
    search_fields = ('sender__username', 'receiver__username', 'sender__phone', 'receiver__phone')
    # Les champs suivants sont en lecture seule car ils sont gérés par la logique de l'application
    readonly_fields = ('created_at', 'final_amount', 'sender', 'receiver', 'amount', 'discount_code_used', 'transaction_type')

    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'amount', 'final_amount', 'discount_code_used', 'status', 'transaction_type')
        }),
        ('Informations sur la date', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle DiscountCode.
    Permet aux administrateurs de créer et gérer les codes de réduction.
    """
    list_display = (
        'code', 'discount_percentage', 'fixed_amount_discount', # 'description' a été supprimé ici
        'max_uses', 'uses_count', 'is_active', 'valid_from', 'valid_until', 'created_by'
    )
    list_filter = ('is_active', 'valid_from', 'valid_until', 'created_by')
    search_fields = ('code',) # 'description' a été supprimé ici
    # Les champs suivants sont en lecture seule car ils sont générés automatiquement ou gérés par l'application
    readonly_fields = ('code', 'uses_count', 'created_by', 'valid_from')

    fieldsets = (
        (None, {
            'fields': (('discount_percentage', 'fixed_amount_discount'),) # 'description' a été supprimé ici
        }),
        ('Utilisation et Validité', {
            'fields': ('max_uses', 'is_active', 'valid_until')
        }),
        ('Informations Automatiques', {
            'fields': ('code', 'uses_count', 'valid_from', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Assigner l'utilisateur actuel comme créateur lors de la création d'un nouveau code
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
