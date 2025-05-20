from rest_framework import serializers
from .models import Transaction, DiscountCode  # Importez DiscountCode
from users.models import User
from django.utils import timezone
from decimal import Decimal


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Transaction.
    """
    receiver = serializers.CharField(write_only=True, label="Bénéficiaire (téléphone ou nom d'utilisateur)")
    sender_username = serializers.CharField(source='sender.username', read_only=True,
                                            label="Nom d'utilisateur de l'expéditeur")
    receiver_username = serializers.CharField(source='receiver.username', read_only=True,
                                              label="Nom d'utilisateur du bénéficiaire")
    discount_code = serializers.CharField(write_only=True, required=False, allow_blank=True,
                                          label="Code de réduction")  # Nouveau champ

    class Meta:
        model = Transaction
        fields = ['id', 'sender_username', 'receiver', 'receiver_username', 'amount', 'final_amount', 'discount_code',
                  'status', 'created_at']
        read_only_fields = ['sender_username', 'receiver_username', 'final_amount', 'status', 'created_at']


class DiscountCodeSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création et la gestion des codes de réduction.
    """

    class Meta:
        model = DiscountCode
        fields = ['id', 'code', 'description', 'discount_percentage', 'fixed_amount_discount',
                  'max_uses', 'uses_count', 'valid_from', 'valid_until', 'is_active', 'created_by']
        read_only_fields = ['code', 'uses_count', 'created_by']  # Code et uses_count sont gérés automatiquement

    def validate(self, data):
        # Valider qu'au moins un type de réduction est spécifié
        if data.get('discount_percentage') is None and data.get('fixed_amount_discount') is None:
            raise serializers.ValidationError(
                "Vous devez spécifier un pourcentage de réduction ou un montant fixe de réduction.")

        # Valider qu'un seul type de réduction est spécifié
        if data.get('discount_percentage') is not None and data.get('fixed_amount_discount') is not None:
            raise serializers.ValidationError(
                "Vous ne pouvez pas spécifier à la fois un pourcentage et un montant fixe de réduction.")

        # Valider les dates
        valid_from = data.get('valid_from')
        valid_until = data.get('valid_until')
        if valid_from and valid_until and valid_from > valid_until:
            raise serializers.ValidationError(
                "La date de début de validité ne peut pas être postérieure à la date de fin.")

        return data

    def create(self, validated_data):
        # Le champ 'created_by' sera défini dans la vue
        return super().create(validated_data)