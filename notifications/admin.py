from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = ('user', 'message', 'notification_type', 'is_read', 'created_at', 'transaction')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at', 'user', 'transaction')

    fieldsets = (
        (None, {
            'fields': ('user', 'message', 'notification_type', 'transaction')
        }),
        ('Statut et Date', {
            'fields': ('is_read', 'created_at'),
            'classes': ('collapse',)
        }),
    )
