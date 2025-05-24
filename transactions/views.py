# transactions/views.py
from rest_framework import generics, views, response, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Transaction, DiscountCode, TRANSACTION_TYPE_CHOICES
from .serializers import TransactionSerializer, DiscountCodeSerializer, InitiateWithdrawalSerializer
from wallets.models import Wallet
from django.db import transaction
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from users.models import User  # Assurez-vous que User est importé
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal

# Importez la fonction d'envoi de notification depuis core.utils
from core.utils import send_notification_to_user


class InitiateTransactionView(views.APIView):
    """
    Vue pour initier une transaction de transfert d'argent (envoi).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        montant_initial = serializer.validated_data['amount']
        receiver_identifier = serializer.validated_data['receiver']
        discount_code_str = serializer.validated_data.get('discount_code')

        final_amount = montant_initial
        discount_code_obj = None

        # Logique d'application du code de réduction (inchangée)
        if discount_code_str:
            try:
                discount_code_obj = DiscountCode.objects.get(
                    code=discount_code_str,
                    is_active=True,
                    uses_count__lt=models.F('max_uses')
                )
                if discount_code_obj.valid_until and discount_code_obj.valid_until < timezone.now():
                    raise ValidationError("Le code de réduction a expiré.")

                if discount_code_obj.valid_from and discount_code_obj.valid_from > timezone.now():
                    raise ValidationError("Le code de réduction n'est pas encore actif.")

                if discount_code_obj.discount_percentage:
                    reduction = montant_initial * (discount_code_obj.discount_percentage / Decimal(100))
                    final_amount = montant_initial - reduction
                elif discount_code_obj.fixed_amount_discount:
                    final_amount = montant_initial - discount_code_obj.fixed_amount_discount
                    if final_amount < 0:
                        final_amount = Decimal(0.00)

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

        # Vérifier si l'expéditeur a suffisamment de fonds
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

                if discount_code_obj:
                    discount_code_obj.uses_count = models.F('uses_count') + 1
                    discount_code_obj.save(update_fields=['uses_count'])
                    discount_code_obj.refresh_from_db()

                # Créer la transaction
                transaction_obj = Transaction.objects.create(
                    sender=request.user,
                    receiver=beneficiaire,
                    amount=montant_initial,
                    final_amount=final_amount,
                    discount_code_used=discount_code_obj,
                    status='success',
                    transaction_type='send'
                )

                # Notifications après transaction réussie
                message_expediteur = f"Votre transfert de {montant_initial} à {beneficiaire.username} a été effectué avec succès. Montant débité : {final_amount}."
                send_notification_to_user(request.user, message_expediteur, notification_type='transaction',
                                          transaction_obj=transaction_obj)

                message_beneficiaire = f"Vous avez reçu {final_amount} de {request.user.username}."
                send_notification_to_user(beneficiaire, message_beneficiaire, notification_type='transaction',
                                          transaction_obj=transaction_obj)

        except Exception as e:
            if 'transaction_obj' in locals():
                transaction_obj.status = 'failed'
                transaction_obj.save()
            raise ValidationError(f"Erreur lors de la transaction : {e}")

        response_serializer = TransactionSerializer(transaction_obj)
        return response.Response(response_serializer.data, status=status.HTTP_201_CREATED)


class InitiateWithdrawalView(views.APIView):
    """
    Vue pour initier une demande de retrait d'argent du portefeuille de l'utilisateur,
    avec vérification du code PIN.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = InitiateWithdrawalSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        pin_code = serializer.validated_data['pin_code']

        # --- CORRECTION ICI : Accéder au PIN via le UserProfile ---
        if not hasattr(request.user, 'profile') or not request.user.profile.transaction_pin:
            raise AuthenticationFailed("Code PIN de transaction non défini. Veuillez le définir d'abord.")

        if not request.user.profile.check_transaction_pin(pin_code):
            raise AuthenticationFailed("Code PIN incorrect.")
        # ----------------------------------------------------------

        user_wallet = request.user.wallet

        if user_wallet.balance < amount:
            raise ValidationError("Fonds insuffisants pour le retrait.")

        try:
            with transaction.atomic():
                user_wallet.balance -= amount
                user_wallet.save()

                withdrawal_transaction = Transaction.objects.create(
                    sender=request.user,
                    receiver=request.user,
                    amount=amount,
                    final_amount=amount,
                    status='pending',
                    transaction_type='withdrawal'
                )

                message_retrait = f"Votre demande de retrait de {amount} est en cours de traitement."
                send_notification_to_user(request.user, message_retrait, notification_type='transaction',
                                          transaction_obj=withdrawal_transaction)

                return response.Response({
                    "message": "Demande de retrait initiée avec succès. En attente de confirmation.",
                    "transaction_id": withdrawal_transaction.id,
                    "amount": amount
                }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            if 'withdrawal_transaction' in locals():
                withdrawal_transaction.status = 'failed'
                withdrawal_transaction.save()
            raise ValidationError(f"Erreur lors de l'initiation du retrait : {e}")


class TransactionHistoryView(generics.ListAPIView):
    """
    Vue pour récupérer l'historique des transactions de l'utilisateur connecté.
    Affiche les transactions où l'utilisateur est expéditeur ou bénéficiaire.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('-created_at')


class DiscountCodeCreateView(generics.CreateAPIView):
    """
    Vue pour créer un nouveau code de réduction.
    Accessible uniquement aux administrateurs.
    """
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DiscountCodeListView(generics.ListAPIView):
    """
    Vue pour lister tous les codes de réduction.
    Accessible uniquement aux administrateurs.
    """
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminUser]
