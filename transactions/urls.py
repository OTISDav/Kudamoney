from django.urls import path
from .views import InitiateTransactionView, TransactionHistoryView, DiscountCodeCreateView, DiscountCodeListView # Importez les nouvelles vues

urlpatterns = [
    path('initiate/', InitiateTransactionView.as_view(), name='initiate_transaction'),
    path('history/', TransactionHistoryView.as_view(), name='transaction_history'),
    # path('discount-codes/create/', DiscountCodeCreateView.as_view(), name='create_discount_code'), # Nouvelle URL pour créer
    # path('discount-codes/', DiscountCodeListView.as_view(), name='list_discount_codes'), # Nouvelle URL pour lister
]