from django.db import models
from rest_framework import generics, views, response, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Transaction, DiscountCode
from .serializers import TransactionSerializer, DiscountCodeSerializer
from wallets.models import Wallet
from django.db import transaction
from rest_framework.exceptions import ValidationError
from users.models import User
from django.db.models import Q
from django.utils import timezone


class InitiateTransactionView(views.APIView):
    """
    Vue pour initier une transaction de transfert d'argent.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        montant_initial = serializer.validated_data['amount']
        receiver_identifier = serializer.validated_data['receiver']
        discount_code_str = serializer.validated_data.get('discount_code')  # Récupérer le code de réduction

        final_amount = montant_initial
        discount_code_obj = None

        # Logique d'application du code de réduction
        if discount_code_str:
            try:
                discount_code_obj = DiscountCode.objects.get(
                    code=discount_code_str,
                    is_active=True,
                    uses_count__lt=models.F('max_uses')  # Vérifie si le nombre d'utilisations n'a pas été dépassé
                )
                # Vérifier la validité par date
                if discount_code_obj.valid_until and discount_code_obj.valid_until < timezone.now():
                    raise ValidationError("Le code de réduction a expiré.")

                if discount_code_obj.valid_from and discount_code_obj.valid_from > timezone.now():
                    raise ValidationError("Le code de réduction n'est pas encore actif.")

                # Appliquer la réduction
                if discount_code_obj.discount_percentage:
                    reduction = montant_initial * (discount_code_obj.discount_percentage / Decimal(100))
                    final_amount = montant_initial - reduction
                elif discount_code_obj.fixed_amount_discount:
                    final_amount = montant_initial - discount_code_obj.fixed_amount_discount
                    if final_amount < 0:  # S'assurer que le montant final n'est pas négatif
                        final_amount = Decimal(0.00)

                # S'assurer que le montant final ne dépasse pas le montant initial
                if final_amount > montant_initial:
                    final_amount = montant_initial

            except DiscountCode.DoesNotExist:
                raise ValidationError("Code de réduction invalide ou inactif.")
            except Exception as e:
                raise ValidationError(f"Erreur lors de l'application du code de réduction : {e}")

        # Vérifier si le bénéficiaire existe
        try:
            beneficiaire = User.objects.get(Q(phone=receiver_identifier) | Q(username=receiver_identifier))
        except User.DoesNotExist:
            raise ValidationError("Le bénéficiaire n'existe pas.")

        # Vérifier si l'expéditeur a suffisamment de fonds (en utilisant le montant final)
        expediteur_wallet = request.user.wallet
        if expediteur_wallet.balance < final_amount:
            raise ValidationError("Fonds insuffisants.")

        # Débiter le compte de l'expéditeur et créditer celui du bénéficiaire
        try:
            with transaction.atomic():
                expediteur_wallet.balance -= final_amount
                expediteur_wallet.save()

                beneficiaire_wallet, created = Wallet.objects.get_or_create(user=beneficiaire)
                beneficiaire_wallet.balance += final_amount
                beneficiaire_wallet.save()

                # Incrémenter le compteur d'utilisation du code de réduction
                if discount_code_obj:
                    discount_code_obj.uses_count = models.F('uses_count') + 1
                    discount_code_obj.save(update_fields=['uses_count'])
                    # Recharger l'objet pour obtenir la valeur mise à jour si nécessaire
                    discount_code_obj.refresh_from_db()

                # Créer la transaction
                transaction_obj = Transaction.objects.create(
                    sender=request.user,
                    receiver=beneficiaire,
                    amount=montant_initial,  # Montant initial avant réduction
                    final_amount=final_amount,  # Montant réel débité/crédité
                    discount_code_used=discount_code_obj,  # Associer le code utilisé
                    status='success'
                )
        except Exception as e:
            if 'transaction_obj' in locals():
                transaction_obj.status = 'failed'
                transaction_obj.save()
            raise ValidationError(f"Erreur lors de la transaction : {e}")

        response_serializer = TransactionSerializer(transaction_obj)
        return response.Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TransactionHistoryView(generics.ListAPIView):
    """
    Vue pour récupérer l'historique des transactions de l'utilisateur connecté.
    Affiche les transactions où l'utilisateur est expéditeur ou bénéficiaire.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-created_at')


class DiscountCodeCreateView(generics.CreateAPIView):
    """
    Vue pour créer un nouveau code de réduction.
    Accessible uniquement aux administrateurs.
    """
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # Assigner l'utilisateur connecté (admin) comme créateur du code
        serializer.save(created_by=self.request.user)


class DiscountCodeListView(generics.ListAPIView):
    """
    Vue pour lister tous les codes de réduction.
    Accessible uniquement aux administrateurs.
    """
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminUser]

