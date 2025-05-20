from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import Wallet
from .serializers import WalletSerializer


class WalletView(generics.RetrieveAPIView):
    """
    Vue pour récupérer le portefeuille de l'utilisateur connecté.
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retourne le portefeuille de l'utilisateur authentifié.
        """
        try:
            return self.request.user.wallet
        except Wallet.DoesNotExist:
            raise NotFound("Portefeuille non trouvé pour cet utilisateur.")
