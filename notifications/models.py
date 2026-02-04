from django.db import models
from django.conf import settings
from django.utils import timezone

NOTIFICATION_TYPE_CHOICES = (
    ('transaction', 'Transaction'),
    ('kyc_status', 'Statut KYC'),
    ('promotion', 'Promotion'),
    ('system', 'Système'),
    ('otp', 'OTP'),
)

class Notification(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name="Utilisateur")
    message = models.TextField(verbose_name="Message")
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES, default='system', verbose_name="Type de notification")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    transaction = models.ForeignKey('transactions.Transaction', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Transaction associée")

    def __str__(self):
        return f"Notification pour {self.user.username} - {self.notification_type} - {self.message[:50]}..."

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']