from rest_framework import serializers
from .models import User, UserProfile, OTPCode
from django.utils import timezone

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
    user = SimpleUserSerializer(read_only=True)
    kyc_photo_id_url = serializers.SerializerMethodField()
    kyc_selfie_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user',
            'kyc_photo_id_url', 'kyc_photo_id_num',
            'kyc_selfie_url', 'is_verified'
        ]

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
