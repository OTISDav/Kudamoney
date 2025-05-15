from rest_framework import serializers
from .models import User, UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import OTPCode



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'pays', 'first_name', 'last_name', 'email')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('phone', 'password', 'pays', 'username')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle UserProfile.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # Change ici

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'kyc_photo_id', 'kyc_photo_id_num', 'kyc_selfie', 'is_verified')
        read_only_fields = ('is_verified',)


class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, write_only=True)
    otp = serializers.CharField(max_length=6, write_only=True)

    def validate(self, data):
        phone = data.get('phone')
        otp = data.get('otp')

        #  vérifier si l'utilisateur existe
        try:
            user = User.objects.get(phone=phone)  # Utilisez User ici
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")

        #  vérifier si l'OTP est valide et n'a pas expiré (exemple : 5 minutes)
        try:
            otp_code = OTPCode.objects.get(user=user, code=otp)
            from django.utils import timezone
            if (timezone.now() - otp_code.created_at).seconds > 300:  # 5 minutes
                otp_code.delete()
                raise serializers.ValidationError("OTP expiré.")
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError("OTP invalide.")

        data['user'] = user  # Ajouter l'utilisateur validé aux données
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['phone'] = user.phone
        token['pays'] = user.pays
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user_data = UserSerializer(user).data
        data['user'] = user_data
        return data