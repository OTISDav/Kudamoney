import random

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status, views, response
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile, OTPCode
from .serializers import OTPSerializer, UserProfileSerializer



def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone, otp):
    # Plutôt que d'envoyer un SMS, afficher l'OTP dans la console
    print(f"OTP pour {phone}: {otp}")
    """
    # envoi de SMS avec Twilio 
    from twilio.rest import Client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        to=phone,
        from_=settings.TWILIO_PHONE_NUMBER,
        body=f"Votre code de vérification est : {otp}",
    )
    print(message.sid)
    """
    pass # laisser vide pour ne pas envoyer de SMS


class UserRegistrationView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        password = request.data.get('password')
        pays = request.data.get('pays')
        username = request.data.get('username')

        if not phone or not password or not pays or not username:
            return response.Response({"error": "Tous les champs sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Créez l'utilisateur
        user = User.objects.create_user(phone=phone, password=password, pays=pays, username=username)

        # Générez un OTP
        otp = generate_otp()
        OTPCode.objects.create(user=user, code=otp)
        send_otp(phone, otp)  # Utilisez la fonction d'envoi d'OTP

        return response.Response({
            "message": "Utilisateur inscrit avec succès. OTP envoyé pour vérification."
        }, status=status.HTTP_201_CREATED)



class UserOTPVerificationView(views.APIView):
    serializer_class = OTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            # Supprimer l'OTP après vérification
            OTPCode.objects.filter(user=user).delete()
            # Générer un token JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return response.Response({
                'access_token': access_token,
                'refresh_token': str(refresh),
                'message': 'OTP vérifié avec succès. Utilisateur connecté.'
            }, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(views.APIView):
    """
    Vue pour la connexion d'un utilisateur.
    """
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return response.Response({"error": "Numéro de téléphone et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, phone=phone, password=password)
        # Utilisez authenticate
        if user is not None:
            # Générer un OTP
            otp = generate_otp()
            OTPCode.objects.create(user=user, code=otp)
            send_otp(phone, otp)  # Utilisez la fonction d'envoi d'OTP

            return response.Response({
                "message": "Connexion réussie. OTP envoyé pour vérification."
            }, status=status.HTTP_200_OK)
        else:
            return response.Response({"error": "Numéro de téléphone ou mot de passe invalide."}, status=status.HTTP_401_UNAUTHORIZED)



class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue pour récupérer et mettre à jour le profil de l'utilisateur connecté.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user



class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]  # Seulement pour les administrateurs



class AdminVerifyProfileView(generics.UpdateAPIView):
    """
    Vue pour permettre à un administrateur de vérifier un profil utilisateur.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser] # Seul un admin peut accéder

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_verified = True # L'admin met le profil à True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)