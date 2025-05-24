# support/models.py
from django.db import models
from django.conf import settings

class Ticket(models.Model):
    """
    Modèle représentant un ticket de support client.
    """
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('in_progress', 'En cours'),
        ('closed', 'Fermé'),
        ('resolved', 'Résolu'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets',
        verbose_name="Utilisateur"
    )
    subject = models.CharField(max_length=255, verbose_name="Sujet")
    description = models.TextField(verbose_name="Description")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Priorité"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière Mise à Jour")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ticket de Support"
        verbose_name_plural = "Tickets de Support"

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} ({self.get_status_display()})"

class Message(models.Model):
    """
    Modèle représentant un message (réponse).
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Ticket"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_support_messages',
        verbose_name="Expéditeur"
    )
    content = models.TextField(verbose_name="Contenu du message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'Envoi")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Message de Support"
        verbose_name_plural = "Messages de Support"

    def __str__(self):
        return f"Message sur Ticket #{self.ticket.id} par {self.sender.username} le {self.created_at.strftime('%Y-%m-%d %H:%M')}"
