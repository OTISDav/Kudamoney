from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Wallet.
    """
    user = serializers.SlugRelatedField(slug_field='username', read_only=True, label="Utilisateur")

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance']
        read_only_fields = ['user', 'balance']