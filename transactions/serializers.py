# transactions/serializers.py
from rest_framework import serializers
from .models import Transaction, DiscountCode
from users.models import User # Importez User
from decimal import Decimal

class TransactionSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    discount_code_used_code = serializers.CharField(source='discount_code_used.code', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['sender', 'receiver', 'status', 'final_amount', 'transaction_type', 'discount_code_used', 'created_at', 'updated_at']

class InitiateWithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    pin_code = serializers.CharField(max_length=6)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à zéro.")
        # Ajoutez d'autres validations, par exemple, limites de retrait
        return value

    def validate_pin_code(self, value):
        if not value.isdigit() or not (4 <= len(value) <= 6):
            raise serializers.ValidationError("Le code PIN doit être composé de 4 à 6 chiffres.")
        return value


class DiscountCodeSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = DiscountCode
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by', 'uses_count']


class RechargeSerializer(serializers.Serializer): # NOUVEAU : Serializer pour la recharge
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant de la recharge doit être supérieur à zéro.")
        # Vous pouvez ajouter ici des règles métier pour les montants min/max de recharge
        return value
