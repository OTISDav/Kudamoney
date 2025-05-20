from django.contrib import admin
from .models import DiscountCode, Transaction # Importez le modèle Transaction

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle DiscountCode.
    Permet aux administrateurs de créer et gérer les codes de réduction.
    """
    list_display = (
        'code', 'description', 'discount_percentage', 'fixed_amount_discount',
        'max_uses', 'uses_count', 'is_active', 'valid_from', 'valid_until', 'created_by'
    )
    list_filter = ('is_active', 'valid_from', 'valid_until', 'created_by')
    search_fields = ('code', 'description')
    readonly_fields = ('code', 'uses_count', 'created_by', 'valid_from') # Ces champs sont auto-générés ou mis à jour par le système

    fieldsets = (
        (None, {
            'fields': ('description', ('discount_percentage', 'fixed_amount_discount'))
        }),
        ('Utilisation et Validité', {
            'fields': ('max_uses', 'is_active', 'valid_until')
        }),
        ('Informations Automatiques', {
            'fields': ('code', 'uses_count', 'valid_from', 'created_by'),
            'classes': ('collapse',) # Masque ces champs par défaut pour plus de clarté
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Définit automatiquement l'utilisateur qui a créé le code lors de la sauvegarde.
        """
        if not obj.pk: # Si c'est une nouvelle instance (création)
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle Transaction.
    Permet aux administrateurs de voir et gérer les transactions.
    """
    list_display = (
        'sender', 'receiver', 'amount', 'final_amount', 'discount_code_used',
        'status', 'created_at'
    )
    list_filter = ('status', 'created_at', 'discount_code_used')
    search_fields = ('sender__username', 'receiver__username', 'sender__phone', 'receiver__phone')
    readonly_fields = ('created_at', 'final_amount', 'sender', 'receiver', 'amount', 'discount_code_used') # Les transactions ne sont pas modifiables après création

    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'amount', 'final_amount', 'discount_code_used', 'status')
        }),
        ('Informations sur la date', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

