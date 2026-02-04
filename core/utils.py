from notifications.models import Notification
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.views import exception_handler
from twilio.rest import Client
from django.conf import settings

def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response

def send_notification_to_user(user, message, notification_type='system', transaction_obj=None):

    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        transaction=transaction_obj
    )
    print(f"Notification créée pour {user.username} ({notification_type}): {message}")

# def send_notification_to_user(user, message, notification_type='system', transaction_obj=None):
#
#     Notification.objects.create(
#         user=user,
#         message=message,
#         notification_type=notification_type,
#         transaction=transaction_obj
#     )
#     print(f"Notification créée pour {user.username} ({notification_type}): {message}")
#
#     if user.phone:
#         try:
#             client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#             sms = client.messages.create(
#                 body=message,
#                 from_=settings.TWILIO_PHONE_NUMBER,
#                 to=user.phone
#             )
#             print(f"SMS envoyé à {user.phone}: SID {sms.sid}")
#         except Exception as e:
#             print(f"Erreur en envoyant le SMS: {e}")
#
def get_exchange_rate(source_currency, target_currency):

    if source_currency == target_currency:
        return Decimal('1.00')

    if (source_currency == 'XAF' and target_currency == 'XOF') or \
            (source_currency == 'XOF' and target_currency == 'XAF'):
        return Decimal('1.00')

    raise ValueError(f"Taux de change non défini pour {source_currency} vers {target_currency}")

def convert_currency(amount, source_currency, target_currency):

    if source_currency == target_currency:
        return amount, Decimal('0.00')

    rate = get_exchange_rate(source_currency, target_currency)
    converted_amount = amount * rate
    conversion_fee_percentage = Decimal('0.005')
    conversion_fee = amount * conversion_fee_percentage

    return converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), conversion_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_fee(amount, transaction_type, source_currency=None, target_currency=None):

    platform_fee = Decimal('0.00')

    if transaction_type == 'recharge':
        platform_fee = amount * Decimal('0.01')
    elif transaction_type == 'withdrawal':
        platform_fee = amount * Decimal('0.02')
    elif transaction_type == 'send':
        platform_fee = Decimal('0.00')

    return platform_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
