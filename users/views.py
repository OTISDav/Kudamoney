# users/views.py
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


def generate_otp():
    """Génère un code OTP aléatoire de 6 chiffres."""
    return str(random.randint(100000, 999999))


def send_otp(phone, otp):
    """
    Simule l'envoi d'un OTP par SMS en l'affichant dans la console.
    À remplacer par une intégration SMS réelle.
    """
    print(f"OTP envoyé à {phone} : {otp}")
    # Ici, vous intégreriez votre service SMS réel (ex: Twilio)
    pass


class UserRegistrationView(views.APIView):
    """
    Vue pour l'inscription d'un nouvel utilisateur.
    Elle gère également l'upload initial des documents KYC et l'application du code de parrainage.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Générer et envoyer l'OTP pour vérification du numéro de téléphone
            otp = generate_otp()
            OTPCode.objects.create(user=user, code=otp)
            send_otp(user.phone, otp)

            # Notification de bienvenue après inscription
            message_bienvenue = f"Bienvenue {user.username} ! Votre compte a été créé avec succès."
            send_notification_to_user(user, message_bienvenue, notification_type='system')

            return Response({
                "message": "Utilisateur créé. OTP envoyé pour vérification.",
                "user_id": user.id  # Utile pour le débogage ou les flux client
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOTPVerificationView(views.APIView):
    """
    Vue pour vérifier le code OTP et authentifier l'utilisateur.
    """
    serializer_class = OTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Supprimer l'OTP après vérification réussie
            OTPCode.objects.filter(user=user).delete()

            # Générer les tokens JWT pour l'utilisateur
            refresh = RefreshToken.for_user(user)

            # Notification de bienvenue/connexion après vérification OTP
            message_bienvenue = f"Bienvenue de retour {user.username} ! Vous êtes connecté."
            send_notification_to_user(user, message_bienvenue, notification_type='system')

            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'message': "OTP vérifié. Connexion réussie."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(views.APIView):
    """
    Vue pour la connexion de l'utilisateur.
    Envoie un OTP pour la vérification à deux facteurs avant de renvoyer les tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return Response({"error": "Téléphone et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                # Générer et envoyer l'OTP pour la connexion
                otp = generate_otp()
                OTPCode.objects.create(user=user, code=otp)
                send_otp(phone, otp)
                return Response({
                    "message": "OTP envoyé pour vérification. Veuillez vérifier votre téléphone.",
                    "user_id": user.id  # Utile pour le débogage
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Mot de passe incorrect."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(views.APIView):
    """
    Vue pour récupérer les détails du profil de l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profil non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    @method_decorator(csrf_exempt, name='dispatch')
    class KYCUploadView(views.APIView):
        """
        Vue pour télécharger les documents KYC (photo d'identité, selfie, numéro d'identité).
        Accessible sans authentification pour les utilisateurs venant de s'inscrire.
        """
        parser_classes = [MultiPartParser, FormParser]
        permission_classes = [AllowAny]

        def post(self, request, user_id, *args, **kwargs):
            try:
                profile = UserProfile.objects.get(user_id=user_id)
            except UserProfile.DoesNotExist:
                return Response({"error": "UserProfile non trouvé pour cet utilisateur."},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = KYCUploadSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'message': 'KYC envoyé avec succès. Votre profil sera vérifié par un administrateur.'},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(views.APIView):
    """
    Vue pour permettre à l'utilisateur connecté de changer son mot de passe.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Mot de passe changé avec succès."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminVerifyProfileView(generics.UpdateAPIView):
    """
    Vue pour permettre à un administrateur de vérifier un profil utilisateur KYC.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer  # Utilisez UserProfileSerializer pour la réponse
    permission_classes = [permissions.IsAdminUser]  # Seul un admin peut accéder

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_verified = True  # L'admin met le profil à True
        instance.save()
        serializer = self.get_serializer(instance, context={'request': request})  # Passez le contexte
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferralCodeView(generics.RetrieveAPIView):
    """
    Vue pour qu'un utilisateur authentifié récupère son code de parrainage.
    Si le code n'existe pas, il est créé automatiquement.
    """
    serializer_class = ReferralCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        # Récupérer ou créer le code de parrainage pour l'utilisateur
        referral_code, created = ReferralCode.objects.get_or_create(referrer=user)
        return referral_code


class SetTransactionPinView(views.APIView):
    """
    Vue pour définir ou changer le code PIN de transaction de l'utilisateur.
    """
    serializer_class = SetTransactionPinSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Code PIN de transaction défini/modifié avec succès."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# La vue UserListView n'est pas strictement nécessaire si elle n'est pas utilisée,
# mais je la garde pour la complétude si vous en avez besoin pour l'admin ou autre.
class UserListView(generics.ListAPIView):
    """
    Vue pour lister tous les utilisateurs.
    Accessible uniquement aux administrateurs.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer  # Ou SimpleUserSerializer si vous voulez moins de détails
    permission_classes = [permissions.IsAdminUser]
