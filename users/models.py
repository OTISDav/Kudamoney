from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
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
    phone = models.CharField(max_length=20, unique=True, verbose_name="Numéro de téléphone")
    pays = models.CharField(max_length=50, verbose_name="Pays")

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Groupes',
        blank=True,
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Permissions',
        blank=True,
        related_name="custom_user_set",
        related_query_name="user",
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone', 'pays']

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Utilisateur")
    kyc_photo_id = models.ImageField(upload_to='kyc/', verbose_name="Photo de la pièce d'identité")
    kyc_photo_id_num = models.CharField(max_length=50, verbose_name="Numéro de la pièce d'identité", blank=True, null=True)
    kyc_selfie = models.ImageField(upload_to='kyc/', verbose_name="Selfie KYC")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")

    def __str__(self):
        return f"Profil utilisateur #{self.user_id}"


class OTPCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6, verbose_name="Code OTP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"OTP pour {self.user.phone} : {self.code}"

    class Meta:
        verbose_name = "Code OTP"
        verbose_name_plural = "Codes OTP"
