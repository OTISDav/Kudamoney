# users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
import uuid
from django.contrib.auth.hashers import make_password, check_password  # Pour hacher et vérifier le PIN


class UserManager(BaseUserManager):
    """
    Manager personnalisé pour le modèle User, permettant la création d'utilisateurs
    et de superutilisateurs avec les champs 'username', 'phone' et 'pays'.
    """

    def create_user(self, username, phone, pays, password=None, **extra_fields):
        if not phone:
            raise ValueError('Le numéro de téléphone est obligatoire.')
        if not username:
            raise ValueError('Le nom d\'utilisateur est obligatoire.')
        if not pays:
            raise ValueError('Le pays est obligatoire.')

        user = self.model(username=username, phone=phone, pays=pays, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone, pays, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Le mot de passe est obligatoire pour un superutilisateur.")

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(username=username, phone=phone, pays=pays, password=password, **extra_fields)


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec numéro de téléphone et pays.
    Utilise un UserManager personnalisé pour la création d'utilisateurs.
    """
    phone = models.CharField(max_length=20, unique=True, verbose_name="Numéro de téléphone")
    pays = models.CharField(max_length=50, verbose_name="Pays")

    # Champs ManyToManyField pour éviter les conflits avec le modèle User par défaut de Django
    # lors de l'utilisation d'un modèle utilisateur personnalisé.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Groupes',
        blank=True,
        related_name="custom_user_set",  # Nom de relation personnalisé
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Permissions',
        blank=True,
        related_name="custom_user_set",  # Nom de relation personnalisé
        related_query_name="user",
    )

    objects = UserManager()  # Utilise le manager personnalisé

    USERNAME_FIELD = 'username'  # Définit 'username' comme champ d'identification unique
    REQUIRED_FIELDS = ['phone', 'pays']  # Champs requis lors de la création d'un utilisateur

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    Modèle de profil utilisateur, lié à l'utilisateur par une relation OneToOne.
    Contient les informations KYC et le code PIN de transaction.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Utilisateur")
    kyc_photo_id = models.ImageField(upload_to='kyc/', verbose_name="Photo de la pièce d'identité", null=True,
                                     blank=True)
    kyc_photo_id_num = models.CharField(max_length=50, verbose_name="Numéro de la pièce d'identité", blank=True,
                                        null=True)
    kyc_selfie = models.ImageField(upload_to='kyc/', verbose_name="Selfie KYC", null=True, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")

    # Champ pour le PIN de transaction (haché) - Réintégré pour la fonctionnalité de retrait
    transaction_pin = models.CharField(max_length=128, blank=True, null=True, verbose_name="Code PIN de transaction")

    def set_transaction_pin(self, raw_pin):
        """
        Hache et définit le code PIN de transaction.
        """
        self.transaction_pin = make_password(raw_pin)
        self.save()

    def check_transaction_pin(self, raw_pin):
        """
        Vérifie le code PIN de transaction fourni.
        """
        return check_password(raw_pin, self.transaction_pin)

    def __str__(self):
        return f"Profil de {self.user.username}"


class OTPCode(models.Model):
    """
    Modèle pour stocker les codes OTP (One-Time Password) envoyés aux utilisateurs.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6, verbose_name="Code OTP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"OTP pour {self.user.phone} : {self.code}"

    class Meta:
        verbose_name = "Code OTP"
        verbose_name_plural = "Codes OTP"


class ReferralCode(models.Model):
    """
    Modèle pour gérer les codes de parrainage.
    """
    code = models.CharField(max_length=20, unique=True, default=uuid.uuid4, verbose_name="Code de parrainage")
    referrer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_code',
                                    verbose_name="Parrain")
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, verbose_name="Montant du bonus")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"Code {self.code} par {self.referrer.username}"

    class Meta:
        verbose_name = "Code de Parrainage"
        verbose_name_plural = "Codes de Parrainage"
