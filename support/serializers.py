# support/serializers.py
from rest_framework import serializers
from .models import Ticket, Message
from users.models import User # Assurez-vous d'importer User si nécessaire

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'ticket', 'sender', 'sender_username', 'content', 'created_at']
        read_only_fields = ['sender', 'ticket', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'user', 'user_username', 'subject', 'description',
            'status', 'priority', 'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'updated_at', 'messages']

class AdminTicketSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'user', 'user_username', 'subject', 'description',
            'status', 'priority', 'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'messages']
