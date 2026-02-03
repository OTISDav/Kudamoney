import random
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.views import APIView  # <--- Assurez-vous que cette ligne est présente
from rest_framework.exceptions import AuthenticationFailed

from .models import User, UserProfile, OTPCode, ReferralCode
from .serializers import (
    UserRegistrationSerializer, OTPSerializer,
    UserProfileSerializer, UserSerializer,
    KYCUploadSerializer, ReferralCodeSerializer,
    ChangePasswordSerializer, SetTransactionPinSerializer
)

# Importez la fonction d'envoi de notification depuis core.utils
from core.utils import send_notification_to_user



import logging
from twilio.rest import Client
from django.conf import settings

logger = logging.getLogger(__name__)

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def generate_otp():
    return str(random.randint(100000, 999999))


logger = logging.getLogger(__name__)

def send_otp(phone, otp):

    print(f"OTP DEBUG {phone} : {otp}")

    logger.info(f"OTP DEBUG {phone} : {otp}")

    message_body = f"Votre code OTP est : {otp}"

    try:
        client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )

        print("SMS envoye")

        logger.info(f"SMS envoye a {phone}")

    except Exception as e:

        print("Erreur Twilio : ", e)
        logger.error(f"Erreur Twilio pour {phone} : {e}")



class UserRegistrationView(views.APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp = generate_otp()
            OTPCode.objects.create(user=user, code=otp)
            send_otp(user.phone, otp)

            message_bienvenue = f"Bienvenue {user.username} ! Votre compte a été créé avec succès."
            send_notification_to_user(user, message_bienvenue, notification_type='system')

            return Response({
                "message": "Utilisateur créé. OTP envoyé pour vérification.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOTPVerificationView(views.APIView):

    serializer_class = OTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            OTPCode.objects.filter(user=user).delete()

            refresh = RefreshToken.for_user(user)

            message_bienvenue = f"Bienvenue de retour {user.username} ! Vous êtes connecté."
            send_notification_to_user(user, message_bienvenue, notification_type='system')

            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'message': "OTP vérifié. Connexion réussie."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(views.APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return Response({"error": "Téléphone et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                otp = generate_otp()
                OTPCode.objects.create(user=user, code=otp)
                send_otp(phone, otp)
                return Response({
                    "message": "OTP envoyé pour vérification. Veuillez vérifier votre téléphone.",
                    "user_id": user.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Mot de passe incorrect."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(views.APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profil non trouvé."}, status=status.HTTP_404_NOT_FOUND)



    pass
@method_decorator(csrf_exempt, name='dispatch')
class KYCUploadView(APIView):
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request, user_id, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

        serializer = KYCUploadSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'KYC envoyé avec succès.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(views.APIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Mot de passe changé avec succès."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminVerifyProfileView(generics.UpdateAPIView):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer  #
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_verified = True
        instance.save()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferralCodeView(generics.RetrieveAPIView):

    serializer_class = ReferralCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        referral_code, created = ReferralCode.objects.get_or_create(referrer=user)
        return referral_code


class SetTransactionPinView(views.APIView):

    serializer_class = SetTransactionPinSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Code PIN de transaction défini/modifié avec succès."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserListView(generics.ListAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
