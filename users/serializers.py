from rest_framework import serializers
from .models import User, UserProfile, OTPCode, ReferralCode  # Assurez-vous que ReferralCode est importé
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password  # Importez check_password
from wallets.models import Wallet  # Assurez-vous que Wallet est importé

User = get_user_model()


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
    kyc_photo_id = serializers.ImageField(required=False, allow_null=True)  # Ajout du champ KYC
    kyc_selfie = serializers.ImageField(required=False, allow_null=True)  # Ajout du champ KYC
    kyc_photo_id_num = serializers.CharField(required=False,
                                             allow_blank=True)  # NOUVEAU: Ajout du champ pour le numéro de pièce d'identité
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True,
                                          label="Code de parrainage")  # Réintégré

    class Meta:
        model = User
        fields = (
            'phone', 'password', 'pays', 'username',
            'kyc_photo_id', 'kyc_selfie', 'kyc_photo_id_num',  # Ajout des champs KYC au Meta
            'referral_code'  # Ajout du champ de parrainage
        )


    def create(self, validated_data):
        password = validated_data.pop('password')
        kyc_photo_id = validated_data.pop('kyc_photo_id', None)
        kyc_selfie = validated_data.pop('kyc_selfie', None)
        kyc_photo_id_num = validated_data.pop('kyc_photo_id_num', None)  # Récupérer le numéro de pièce d'identité
        referral_code_str = validated_data.pop('referral_code', None)  # Récupérer le code de parrainage
        pays_data = validated_data.get('pays')

        user = User.objects.create_user(
            phone=validated_data['phone'],
            username=validated_data['username'],
            pays=validated_data['pays']
        )
        user.set_password(password)
        user.save()

        # Créer UserProfile et enregistrer les données KYC
        UserProfile.objects.create(
            user=user,
            kyc_photo_id=kyc_photo_id,
            kyc_selfie=kyc_selfie,
            kyc_photo_id_num=kyc_photo_id_num  # Enregistrer le numéro de pièce d'identité
        )
        # Créer un Wallet pour le nouvel utilisateur avec la bonne devise
        user_currency = 'XOF'  # Devise par défaut
        if pays_data and pays_data.upper() == 'TCHAD':
            user_currency = 'XAF'

        # Créer UN SEUL portefeuille avec la bonne devise
        Wallet.objects.create(user=user, currency=user_currency)

        # Logique de parrainage (réintégrée)
        if referral_code_str:
            try:
                referral_code_obj = ReferralCode.objects.get(code=referral_code_str, is_active=True)
                referrer_user = referral_code_obj.referrer

                # Appliquer le bonus au parrain (referrer)
                referrer_wallet = referrer_user.wallet
                referrer_wallet.balance += referral_code_obj.bonus_amount
                referrer_wallet.save()

                # Appliquer le bonus au filleul (nouvel utilisateur)
                filleul_wallet = user.wallet
                filleul_wallet.balance += referral_code_obj.bonus_amount
                filleul_wallet.save()

            except ReferralCode.DoesNotExist:
                print(f"Code de parrainage invalide ou inactif : {referral_code_str}")

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    kyc_photo_id_url = serializers.SerializerMethodField()
    kyc_selfie_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user',
            'kyc_photo_id_url', 'kyc_photo_id_num',  # Réintégré kyc_photo_id_num
            'kyc_selfie_url', 'is_verified'
        ]
        read_only_fields = ('is_verified',)  # is_verified est en lecture seule

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
        # from .models import OTPCode  # Pas nécessaire si OTPCode est déjà importé en haut
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


class ReferralCodeSerializer(serializers.ModelSerializer):  # Réintégré
    class Meta:
        model = ReferralCode
        fields = ['code', 'bonus_amount', 'is_active', 'created_at']
        read_only_fields = ['code', 'bonus_amount', 'is_active', 'created_at']


class SetTransactionPinSerializer(serializers.Serializer):  # Réintégré
    """
    Serializer pour définir ou changer le code PIN de transaction.
    """
    current_pin = serializers.CharField(max_length=6, write_only=True, required=False, allow_blank=True,
                                        label="Code PIN actuel (si modification)")
    new_pin = serializers.CharField(max_length=6, write_only=True, required=True, label="Nouveau Code PIN")
    confirm_new_pin = serializers.CharField(max_length=6, write_only=True, required=True,
                                            label="Confirmer le nouveau Code PIN")

    def validate(self, data):
        new_pin = data.get('new_pin')
        confirm_new_pin = data.get('confirm_new_pin')
        current_pin = data.get('current_pin')
        user_profile = self.context['request'].user.profile

        if new_pin != confirm_new_pin:
            raise serializers.ValidationError("Le nouveau code PIN et la confirmation ne correspondent pas.")

        if not new_pin.isdigit() or not (4 <= len(new_pin) <= 6):  # Validation pour 4 à 6 chiffres
            raise serializers.ValidationError("Le code PIN doit être composé de 4 à 6 chiffres.")

        # Si un PIN existe déjà, vérifier le PIN actuel
        if user_profile.transaction_pin:
            if not current_pin:
                raise serializers.ValidationError("Le code PIN actuel est requis pour la modification.")
            if not user_profile.check_transaction_pin(current_pin):
                raise serializers.ValidationError("Le code PIN actuel est incorrect.")
        elif current_pin:  # Si aucun PIN n'existe mais un current_pin est fourni
            raise serializers.ValidationError("Aucun code PIN actuel n'est défini.")

        return data

    def save(self, **kwargs):
        user_profile = self.context['request'].user.profile
        new_pin = self.validated_data['new_pin']
        user_profile.set_transaction_pin(new_pin)  # Utilise la méthode du modèle pour hacher et sauvegarder
        return user_profile
