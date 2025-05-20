import random
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile, OTPCode
from .serializers import (
    UserRegistrationSerializer, OTPSerializer,
    UserProfileSerializer, UserSerializer,
    KYCUploadSerializer, ChangePasswordSerializer
)

# Génération aléatoire de code OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Simulation d'envoi OTP
def send_otp(phone, otp):
    print(f"OTP envoyé à {phone} : {otp}")


class UserRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = generate_otp()
            OTPCode.objects.create(user=user, code=otp)
            send_otp(user.phone, otp)
            return Response({
                "message": "Utilisateur créé. OTP envoyé pour vérification.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Vérification OTP
class UserOTPVerificationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            OTPCode.objects.filter(user=user).delete()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'message': "OTP vérifié. Connexion réussie."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Connexion (avec génération OTP)
class UserLoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return Response({"error": "Téléphone et mot de passe requis."}, status=400)

        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                otp = generate_otp()
                OTPCode.objects.create(user=user, code=otp)
                send_otp(phone, otp)
                return Response({"message": "OTP envoyé pour vérification.", "user_id": user.id}, status=200)
            else:
                return Response({"error": "Mot de passe incorrect."}, status=401)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=404)

# ✅ Vue profil utilisateur (authentification requise)
class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profil non trouvé."}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class KYCUploadView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

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
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Mot de passe changé avec succès."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminVerifyProfileView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_verified = True
        instance.save()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
