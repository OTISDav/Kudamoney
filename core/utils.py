# core/utils.py
from notifications.models import Notification
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.views import exception_handler

# Importez d'autres modules nécessaires pour l'envoi réel (ex: Twilio, Firebase)
# from twilio.rest import Client
# from firebase_admin import messaging

def custom_exception_handler(exc, context):
    """
    Gère les erreurs DRF personnalisées.
    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response

def send_notification_to_user(user, message, notification_type='system', transaction_obj=None):
    """
    Crée une notification en base de données et simule un envoi (SMS/Push).
    Cette fonction est centralisée pour être utilisée par toutes les applications.
    """
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        transaction=transaction_obj
    )
    print(f"Notification créée pour {user.username} ({notification_type}): {message}")

    # --- Intégration du service SMS/Push ici ---
    # try:
    #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    #     client.messages.create(
    #         to=user.phone,
    #         from_=settings.TWILIO_PHONE_NUMBER,
    #         body=message
    #     )
    #     print(f"SMS envoyé à {user.phone}")
    # except Exception as e:
    #     print(f"Erreur lors de l'envoi du SMS à {user.phone}: {e}")

    # try:
    #     # Assurez-vous que l'utilisateur a un token FCM enregistré sur son profil
    #     # user_fcm_token = user.profile.fcm_token
    #     # if user_fcm_token:
    #     #     message_fcm = messaging.Message(
    #     #         notification=messaging.Notification(title='Nouvelle Notification', body=message),
    #     #         token=user_fcm_token,
    #     #     )
    #     #     response = messaging.send(message_fcm)
    #     #     print(f"Push notification envoyée : {response}")
    # except Exception as e:
    #     print(f"Erreur lors de l'envoi de la notification push à {user.username}: {e}")
    # -------------------------------------------

def get_exchange_rate(source_currency, target_currency):
    """
    Retourne le taux de change pour la conversion de source_currency à target_currency.
    Pour XAF et XOF, la parité est fixe, mais des frais de conversion peuvent être ajoutés.
    """
    if source_currency == target_currency:
        return Decimal('1.00')

    if (source_currency == 'XAF' and target_currency == 'XOF') or \
            (source_currency == 'XOF' and target_currency == 'XAF'):
        return Decimal('1.00')

    raise ValueError(f"Taux de change non défini pour {source_currency} vers {target_currency}")

def convert_currency(amount, source_currency, target_currency):
    """
    Convertit un montant d'une devise source à une devise cible.
    Retourne le montant converti et le montant des frais de conversion de la plateforme.
    """
    if source_currency == target_currency:
        return amount, Decimal('0.00')

    rate = get_exchange_rate(source_currency, target_currency)
    converted_amount = amount * rate
    conversion_fee_percentage = Decimal('0.005')
    conversion_fee = amount * conversion_fee_percentage

    return converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), conversion_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_fee(amount, transaction_type, source_currency=None, target_currency=None):
    """
    Calcule les frais de plateforme pour une transaction donnée.
    Ces frais sont distincts des frais de conversion.
    """
    platform_fee = Decimal('0.00')

    if transaction_type == 'recharge':
        platform_fee = amount * Decimal('0.01')
    elif transaction_type == 'withdrawal':
        platform_fee = amount * Decimal('0.02')
    elif transaction_type == 'send':
        platform_fee = Decimal('0.00')

    return platform_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
