from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Notification.
    """
    user_username = serializers.CharField(source='user.username', read_only=True, label="Nom d'utilisateur")
    transaction_id = serializers.IntegerField(source='transaction.id', read_only=True, label="ID de transaction", allow_null=True)


    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_username', 'message', 'notification_type', 'is_read', 'created_at', 'transaction_id']
        read_only_fields = ['user', 'created_at', 'transaction_id', 'user_username'] # L'utilisateur est défini par la vue, la date est auto_add

