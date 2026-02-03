# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, UserLoginView, UserProfileView,
    UserOTPVerificationView, KYCUploadView, ChangePasswordView,
    AdminVerifyProfileView, ReferralCodeView, SetTransactionPinView,
    UserListView # Assurez-vous que UserListView est importé si vous le gardez
)

urlpatterns = [
    # Authentification et gestion de compte
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('verify-otp/', UserOTPVerificationView.as_view(), name='user_otp_verification'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profil utilisateur et KYC
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('kyc/<int:user_id>/', KYCUploadView.as_view(), name='user_kyc_upload'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('set-pin/', SetTransactionPinView.as_view(), name='set_transaction_pin'),

    # Parrainage
    path('referral-code/', ReferralCodeView.as_view(), name='get_referral_code'),

    # Vues d'administration
    path('admin/verify-profile/<int:pk>/', AdminVerifyProfileView.as_view(), name='admin_verify_profile'),
    path('admin/list/', UserListView.as_view(), name='user_list_admin'), # Pour lister les utilisateurs (admin)
]
