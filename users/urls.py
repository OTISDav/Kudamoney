from django.urls import path
from .views import (
    UserRegistrationView,
    UserOTPVerificationView,
    UserLoginView,
    UserProfileView,
    AdminVerifyProfileView,
    KYCUploadView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-otp/', UserOTPVerificationView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('kyc/', KYCUploadView.as_view(), name='kyc-upload'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('admin/verify-profile/<int:pk>/', AdminVerifyProfileView.as_view(), name='verify-profile'),
]
