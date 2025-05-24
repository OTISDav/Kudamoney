# wallets/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet', verbose_name="Utilisateur")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Solde")
    # NOUVEAU : Champ pour la devise du portefeuille
    currency = models.CharField(
        max_length=5,
        default='XAF',  # Exemple de devise par défaut (Franc CFA Ouest-Africain pour le Togo)
        verbose_name="Devise"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Mise à Jour")

    class Meta:
        verbose_name = "Portefeuille"
        verbose_name_plural = "Portefeuilles"

    def __str__(self):
        return f"Portefeuille de {self.user.username} - Solde: {self.balance} {self.currency}"

    def deposit(self, amount):
        if not isinstance(amount, (int, float, Decimal)) or amount <= 0:
            raise ValueError("Le montant du dépôt doit être un nombre positif.")
        self.balance += Decimal(amount)
        self.save()
        return self.balance

    def withdraw(self, amount):
        if not isinstance(amount, (int, float, Decimal)) or amount <= 0:
            raise ValueError("Le montant du retrait doit être un nombre positif.")
        if self.balance < Decimal(amount):
            raise ValueError("Fonds insuffisants.")
        self.balance -= Decimal(amount)
        self.save()
        return self.balance
