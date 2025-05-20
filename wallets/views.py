from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Wallet
from .serializers import WalletSerializer

class WalletView(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.wallet