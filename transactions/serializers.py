# transactions/serializers.py
from rest_framework import serializers
from .models import Transaction, DiscountCode
from users.models import User
from django.utils import timezone
from decimal import Decimal

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Transaction (utilisé pour l'historique).
    """
    receiver = serializers.CharField(write_only=True, required=False, allow_blank=True, label="Bénéficiaire (téléphone ou nom d'utilisateur)")
    sender_username = serializers.CharField(source='sender.username', read_only=True, label="Nom d'utilisateur de l'expéditeur")
    receiver_username = serializers.CharField(source='receiver.username', read_only=True, label="Nom d'utilisateur du bénéficiaire")
    discount_code = serializers.CharField(write_only=True, required=False, allow_blank=True, label="Code de réduction")

    class Meta:
        model = Transaction
        fields = ['id', 'sender_username', 'receiver', 'receiver_username', 'amount', 'final_amount', 'discount_code', 'status', 'transaction_type', 'created_at']
        read_only_fields = ['sender_username', 'receiver_username', 'final_amount', 'status', 'created_at', 'transaction_type']


class InitiateWithdrawalSerializer(serializers.Serializer):
    """
    Serializer pour initier une demande de retrait, incluant le code PIN.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'), label="Montant du retrait")
    pin_code = serializers.CharField(max_length=6, write_only=True, required=True, label="Code PIN") # Nouveau champ pour le PIN

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant du retrait doit être positif.")
        return value

    # La validation du PIN lui-même sera faite dans la vue pour accéder à request.user
    # ou vous pouvez ajouter une méthode de validation ici si le PIN est stocké sur UserProfile
    # et accessible via user.profile.check_pin(value)


class DiscountCodeSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création et la gestion des codes de réduction.
    """
    class Meta:
        model = DiscountCode
        fields = ['id', 'code', 'description', 'discount_percentage', 'fixed_amount_discount',
                  'max_uses', 'uses_count', 'valid_from', 'valid_until', 'is_active', 'created_by']
        read_only_fields = ['code', 'uses_count', 'created_by']

    def validate(self, data):
        if data.get('discount_percentage') is None and data.get('fixed_amount_discount') is None:
            raise serializers.ValidationError("Vous devez spécifier un pourcentage de réduction ou un montant fixe de réduction.")

        if data.get('discount_percentage') is not None and data.get('fixed_amount_discount') is not None:
            raise serializers.ValidationError("Vous ne pouvez pas spécifier à la fois un pourcentage et un montant fixe de réduction.")

        valid_from = data.get('valid_from')
        valid_until = data.get('valid_until')
        if valid_from and valid_until and valid_from > valid_until:
            raise serializers.ValidationError("La date de début de validité ne peut pas être postérieure à la date de fin.")

        return data

    def create(self, validated_data):
        return super().create(validated_data)
