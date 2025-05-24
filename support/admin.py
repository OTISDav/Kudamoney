# support/admin.py
from django.contrib import admin
from .models import Ticket, Message

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'priority', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('user__username', 'subject', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user', 'subject', 'description')}),
        ('Statut et Priorité', {'fields': ('status', 'priority')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ticket__subject', 'sender__username', 'content')
    readonly_fields = ('ticket', 'sender', 'created_at') # Champs auto-gérés ou liés

