# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPCode, ReferralCode


# Personnalisation de l'Admin pour le modèle User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle User.
    """
    # Ajoute 'phone' et 'pays' aux champs affichés dans la liste
    list_display = ('username', 'phone', 'pays', 'email', 'is_staff', 'is_active')
    # Ajoute 'phone' et 'pays' aux champs de recherche
    search_fields = ('username', 'phone', 'email')
    # Ajoute 'pays' et 'is_staff' aux filtres
    list_filter = ('is_staff', 'is_active', 'pays')

    # Personnalise les champs affichés lors de l'ajout/modification d'un utilisateur
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations Personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone', 'pays')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    # Les champs requis sont déjà gérés par le UserManager personnalisé


# Personnalisation de l'Admin pour le modèle UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle UserProfile.
    Gère les informations KYC et le PIN de transaction.
    """
    list_display = ('user', 'kyc_photo_id_num', 'is_verified', 'transaction_pin_set')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__phone', 'kyc_photo_id_num')

    # Rendre les champs de fichier et le PIN en lecture seule pour éviter les modifications directes
    # Le PIN est haché, donc il ne peut pas être modifié directement ici.
    # La vérification se fait via l'API, pas l'admin.
    readonly_fields = ('user', 'kyc_photo_id', 'kyc_selfie', 'is_verified', 'transaction_pin')

    fieldsets = (
        (None, {'fields': ('user', 'kyc_photo_id_num', 'is_verified')}),
        ('Documents KYC', {
            'fields': ('kyc_photo_id', 'kyc_selfie'),
            'classes': ('collapse',)  # Masque par défaut pour la clarté
        }),
        ('Code PIN de Transaction', {
            'fields': ('transaction_pin',),  # Afficher le champ haché (lecture seule)
            'classes': ('collapse',)
        }),
    )

    def transaction_pin_set(self, obj):
        """Affiche si le PIN de transaction est défini."""
        return bool(obj.transaction_pin)

    transaction_pin_set.boolean = True
    transaction_pin_set.short_description = "PIN de transaction défini"


# Enregistrement du modèle OTPCode dans l'admin
@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle OTPCode.
    """
    list_display = ('user', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__phone')
    readonly_fields = ('user', 'code', 'created_at')  # OTPs ne doivent pas être modifiés manuellement


# Enregistrement du modèle ReferralCode dans l'admin
@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    """
    Personnalisation de l'interface d'administration pour le modèle ReferralCode.
    """
    list_display = ('code', 'referrer', 'bonus_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'referrer__username', 'referrer__phone')
    readonly_fields = ('code', 'created_at', 'referrer')  # Le code est auto-généré, le créateur est l'utilisateur
