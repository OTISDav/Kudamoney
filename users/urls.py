from django.urls import path
from .views import (
    UserRegistrationView,
    UserOTPVerificationView,
    UserLoginView,
    UserProfileView,
    AdminVerifyProfileView,
    KYCUploadView,
    ChangePasswordView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-otp/', UserOTPVerificationView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('kyc/<int:user_id>/', KYCUploadView.as_view(), name='user_kyc_upload'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('admin/verify-profile/<int:pk>/', AdminVerifyProfileView.as_view(), name='verify-profile'),
]
