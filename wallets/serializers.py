# wallets/serializers.py
from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Wallet.
    """
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'username', 'balance', 'currency', 'created_at', 'updated_at'] # Ajout de 'currency'
        read_only_fields = ['id', 'username', 'balance', 'currency', 'created_at', 'updated_at'] # Le solde et la devise sont gérés par la logique métier

