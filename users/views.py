import random
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile, OTPCode
from .serializers import (
    UserRegistrationSerializer, OTPSerializer,
    UserProfileSerializer, UserSerializer
)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone, otp):
    print(f"OTP envoyé à {phone} : {otp}")
    pass
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
                "message": "Utilisateur créé. OTP envoyé pour vérification."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserOTPVerificationView(views.APIView):
    serializer_class = OTPSerializer
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
                return Response({"message": "OTP envoyé pour vérification."}, status=200)
            else:
                return Response({"error": "Mot de passe incorrect."}, status=401)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=404)

class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user.user
            serializer = UserProfileSerializer(user, context={'request': request})
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profil non trouvé."}, status=404)

class AdminVerifyProfileView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_verified = True
        instance.save()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
