from django.db import models
from django.conf import settings

class Wallet(models.Model):
    """
    Modèle représentant le portefeuille électronique d'un utilisateur.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet', verbose_name="Utilisateur")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Solde")

    def __str__(self):
        return f"Portefeuille de {self.user.username}"

    class Meta:
        verbose_name = "Portefeuille"
        verbose_name_plural = "Portefeuilles"