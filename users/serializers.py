from rest_framework import serializers
from .models import User, UserProfile, OTPCode
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'pays']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'pays', 'first_name', 'last_name', 'email')



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    kyc_photo_id = serializers.ImageField(required=False)  # Ajout du champ KYC
    kyc_selfie = serializers.ImageField(required=False)  # Ajout du champ KYC

    class Meta:
        model = User
        fields = ('phone', 'password', 'pays', 'username', 'kyc_photo_id', 'kyc_selfie') # Ajout des champs au Meta

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Récupérer les données KYC avant la création de l'utilisateur
        kyc_photo_id = validated_data.pop('kyc_photo_id', None)
        kyc_selfie = validated_data.pop('kyc_selfie', None)

        user = User.objects.create_user(phone=validated_data['phone'], username=validated_data['username'],
                                       pays=validated_data['pays'])
        user.set_password(password)
        user.save()

        # Créer UserProfile et enregistrer les données KYC
        profile = UserProfile.objects.create(user=user, kyc_photo_id=kyc_photo_id,
                                             kyc_selfie=kyc_selfie)  # Créer le profil ici
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    kyc_photo_id_url = serializers.SerializerMethodField()
    kyc_selfie_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user',
            'kyc_photo_id_url', 'kyc_photo_id_num',
            'kyc_selfie_url', 'is_verified'
        ]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "phone": obj.user.phone,
            "pays": obj.user.pays
        }

    def get_kyc_photo_id_url(self, obj):
        request = self.context.get('request')
        if obj.kyc_photo_id and request:
            return request.build_absolute_uri(obj.kyc_photo_id.url)
        return None

    def get_kyc_selfie_url(self, obj):
        request = self.context.get('request')
        if obj.kyc_selfie and request:
            return request.build_absolute_uri(obj.kyc_selfie.url)
        return None


class KYCUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['kyc_photo_id', 'kyc_photo_id_num', 'kyc_selfie']


class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, write_only=True)
    otp = serializers.CharField(max_length=6, write_only=True)

    def validate(self, data):
        from .models import OTPCode  # éviter import circulaire
        phone = data.get('phone')
        otp = data.get('otp')

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")

        try:
            otp_code = OTPCode.objects.get(user=user, code=otp)
            if (timezone.now() - otp_code.created_at).seconds > 300:
                otp_code.delete()
                raise serializers.ValidationError("OTP expiré.")
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError("OTP invalide.")

        data['user'] = user
        return data


User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("Le nouveau mot de passe doit être différent de l'ancien.")
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.password = make_password(self.validated_data['new_password'])
        user.save()
        return user
