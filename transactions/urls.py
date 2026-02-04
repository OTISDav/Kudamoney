# transactions/urls.py
from django.urls import path
from .views import (
    InitiateTransactionView,
    TransactionHistoryView,
    InitiateWithdrawalView,
    DiscountCodeCreateView,
    DiscountCodeListView,
    RechargeAccountView # NOUVEAU : Importez la vue de recharge
)

urlpatterns = [
    path('send/', InitiateTransactionView.as_view(), name='initiate_transaction'),
    path('withdraw/', InitiateWithdrawalView.as_view(), name='initiate_withdrawal'),
    path('history/', TransactionHistoryView.as_view(), name='transaction_history'),
    path('discount-codes/create/', DiscountCodeCreateView.as_view(), name='create_discount_code'),
    path('discount-codes/', DiscountCodeListView.as_view(), name='list_discount_codes'),
    path('recharge/', RechargeAccountView.as_view(), name='recharge_account'),
]
