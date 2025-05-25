# wallets/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal

class Wallet(models.Model):
    """
    Modèle représentant le portefeuille électronique d'un utilisateur.
    """
    CURRENCY_CHOICES = [
        ('XOF', 'Franc CFA BCEAO (Togo, Bénin, Burkina Faso, etc.)'),
        ('XAF', 'Franc CFA BEAC (Cameroun, Tchad, Centrafrique, etc.)'),
        # Ajoutez d'autres devises si nécessaire
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name="Utilisateur"
    )
    balance = models.DecimalField(
        max_digits=15, # Augmenté pour plus de précision si nécessaire
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Solde"
    )
    currency = models.CharField( # NOUVEAU CHAMP
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='XOF', # Devise par défaut si non spécifiée à la création
        verbose_name="Devise du portefeuille"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière Mise à Jour")

    class Meta:
        verbose_name = "Portefeuille"
        verbose_name_plural = "Portefeuilles"

    def __str__(self):
        return f"Portefeuille de {self.user.username}: {self.balance} {self.currency}"

    def deposit(self, amount):
        if not isinstance(amount, Decimal) or amount <= 0:
            raise ValueError("Le montant du dépôt doit être un nombre décimal positif.")
        self.balance += amount
        self.save(update_fields=['balance'])

    def withdraw(self, amount):
        if not isinstance(amount, Decimal) or amount <= 0:
            raise ValueError("Le montant du retrait doit être un nombre décimal positif.")
        if self.balance < amount:
            raise ValueError("Fonds insuffisants.")
        self.balance -= amount
        self.save(update_fields=['balance'])
