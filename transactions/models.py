# transactions/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

# Définition des types de transaction
TRANSACTION_TYPE_CHOICES = [
    ('send', 'Send Money'),
    ('receive', 'Receive Money'),
    ('withdrawal', 'Withdrawal'),
    ('recharge', 'Recharge/Deposit'), # NOUVEAU : Ajout du type de transaction pour la recharge
]

class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_transactions', verbose_name="Expéditeur")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='received_transactions', verbose_name="Bénéficiaire")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant Initial")
    final_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant Final (après frais/réductions)")
    status_choices = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending', verbose_name="Statut")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, verbose_name="Type de Transaction")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    discount_code_used = models.ForeignKey('DiscountCode', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Code de réduction utilisé")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Mise à Jour")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"Transaction {self.id}: {self.sender} -> {self.receiver} - {self.amount} ({self.status})"

class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Code de Réduction")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Pourcentage de Réduction")
    fixed_amount_discount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Montant Fixe de Réduction")
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name="Valide à partir de")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="Valide jusqu'à")
    max_uses = models.PositiveIntegerField(default=1, verbose_name="Nombre Maximum d'Utilisations")
    uses_count = models.PositiveIntegerField(default=0, verbose_name="Nombre d'Utilisations Actuelles")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_discount_codes', verbose_name="Créé par")

    class Meta:
        verbose_name = "Code de Réduction"
        verbose_name_plural = "Codes de Réduction"

    def __str__(self):
        return self.code

    def clean(self):
        if self.discount_percentage is not None and self.fixed_amount_discount is not None:
            raise models.ValidationError("Vous ne pouvez pas spécifier à la fois un pourcentage et un montant fixe de réduction.")
        if self.discount_percentage is None and self.fixed_amount_discount is None:
            raise models.ValidationError("Vous devez spécifier soit un pourcentage, soit un montant fixe de réduction.")

    def is_valid(self):
        now = timezone.now()
        return (self.is_active and
                self.uses_count < self.max_uses and
                (self.valid_from is None or self.valid_from <= now) and
                (self.valid_until is None or self.valid_until >= now))

