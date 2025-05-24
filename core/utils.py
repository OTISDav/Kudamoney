from rest_framework.views import exception_handler
from notifications.models import Notification
from rest_framework.exceptions import APIException

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # On vérifie si response.data est un dict avant de modifier
        if isinstance(response.data, dict):
            response.data['status_code'] = response.status_code

            if hasattr(exc, 'detail'):
                response.data['message'] = (
                    exc.detail if isinstance(exc.detail, str)
                    else str(exc.detail)
                )
            else:
                response.data['message'] = str(exc)
    return response



from django.conf import settings


# Importez d'autres modules nécessaires pour l'envoi réel (ex: Twilio, Firebase)
# from twilio.rest import Client
# from firebase_admin import messaging

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
    # Exemple pour SMS avec Twilio (décommentez et configurez settings.py) :
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

    # Exemple pour Push Notification avec Firebase Cloud Messaging (décommentez et configurez Firebase Admin SDK) :
    # try:
    #     # Assurez-vous que l'utilisateur a un token FCM enregistré sur son profil
    #     # user_fcm_token = user.profile.fcm_token # Exemple si vous stockez le token dans UserProfile
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
