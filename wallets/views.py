# wallets/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
            # Cela ne devrait pas arriver si le portefeuille est créé à l'inscription
            # mais c'est une bonne pratique de gérer ce cas.
            return Response({"detail": "Portefeuille non trouvé pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)

