from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPCode, ReferralCode


# Personnalisation de l'Admin pour le modèle User
@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ('username', 'phone', 'pays', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'phone', 'email')
    list_filter = ('is_staff', 'is_active', 'pays')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations Personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone', 'pays')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates Importantes', {'fields': ('last_login', 'date_joined')}),
    )


# Personnalisation de l'Admin pour le modèle UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'kyc_photo_id_num', 'is_verified', 'transaction_pin_set')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__phone', 'kyc_photo_id_num')


    readonly_fields = ('user', 'kyc_photo_id', 'kyc_selfie', 'is_verified', 'transaction_pin')

    fieldsets = (
        (None, {'fields': ('user', 'kyc_photo_id_num', 'is_verified')}),
        ('Documents KYC', {
            'fields': ('kyc_photo_id', 'kyc_selfie'),
            'classes': ('collapse',)
        }),
        ('Code PIN de Transaction', {
            'fields': ('transaction_pin',),
            'classes': ('collapse',)
        }),
    )

    def transaction_pin_set(self, obj):
        return bool(obj.transaction_pin)

    transaction_pin_set.boolean = True
    transaction_pin_set.short_description = "PIN de transaction défini"


# Enregistrement du modèle OTPCode dans l'admin
@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):

    list_display = ('user', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__phone')
    readonly_fields = ('user', 'code', 'created_at')

# Enregistrement du modèle ReferralCode dans l'admin
@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):

    list_display = ('code', 'referrer', 'bonus_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'referrer__username', 'referrer__phone')
    readonly_fields = ('code', 'created_at', 'referrer')  #
