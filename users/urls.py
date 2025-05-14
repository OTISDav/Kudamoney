from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserListView, UserOTPVerificationView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('list/', UserListView.as_view(), name='user_list'),
    path('verify-otp/', UserOTPVerificationView.as_view(), name='verify_otp'), # Ajoutez cette URL
]