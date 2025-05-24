# transactions/models.py
from django.db import models
from django.conf import settings
import uuid # Pour générer des codes uniques

TRANSACTION_STATUS = (
    ('pending', 'En attente'),
    ('success', 'Réussie'),
    ('failed', 'Échouée'),
)

TRANSACTION_TYPE_CHOICES = (
    ('send', 'Envoi'),
    ('receive', 'Réception'),
    ('withdrawal', 'Retrait'),
    ('deposit', 'Dépôt'),
)

class Transaction(models.Model):
    """
    Modèle représentant une transaction financière.
    """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions', verbose_name="Expéditeur")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_transactions', verbose_name="Bénéficiaire")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant final après réduction", null=True, blank=True)
    discount_code_used = models.ForeignKey('DiscountCode', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Code de réduction utilisé")
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending', verbose_name="Statut")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name="Type de transaction", default='send')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"Transaction {self.transaction_type} de {self.sender.username} à {self.receiver.username} - {self.status}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

class DiscountCode(models.Model):
    """
    Modèle pour gérer les codes de réduction/promotionnels.
    """
    code = models.CharField(max_length=40, unique=True, default=uuid.uuid4, verbose_name="Code de réduction")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Pourcentage de réduction")
    fixed_amount_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montant de réduction fixe")
    max_uses = models.IntegerField(default=1, verbose_name="Nombre maximum d'utilisations")
    uses_count = models.IntegerField(default=0, verbose_name="Nombre d'utilisations actuelles")
    valid_from = models.DateTimeField(auto_now_add=True, verbose_name="Valide à partir de")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="Valide jusqu'à")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Créé par")

    def __str__(self):
        return f"Code de réduction: {self.code} ({self.description})"

    class Meta:
        verbose_name = "Code de Réduction"
        verbose_name_plural = "Codes de Réduction"