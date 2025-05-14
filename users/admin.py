from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPCode


@admin.action(description="Supprimer les utilisateurs et leurs profils liés")
def delete_users_and_related(modeladmin, request, queryset):
    for user in queryset:
        user.delete()


class UserAdmin(BaseUserAdmin):
    actions = [delete_users_and_related]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('phone', 'pays', 'email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'pays', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'phone', 'pays', 'is_staff', 'is_superuser')
    search_fields = ('username', 'phone', 'pays')
    ordering = ('username',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'kyc_photo_id_num', 'is_verified')
    search_fields = ('user__username', 'kyc_photo_id_num')
    list_filter = ('is_verified',)

class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__phone', 'code')
    list_filter = ('created_at',)

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(OTPCode, OTPCodeAdmin)
