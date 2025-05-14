from django.contrib.auth.backends import ModelBackend
from users.models import User

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, phone=None, password=None, **kwargs):
        try:
            # Autoriser l'authentification soit par username, soit par phone
            user = None
            if phone:
                user = User.objects.get(phone=phone)
            elif username:
                user = User.objects.get(username=username)
            else:
                return None

            if user and user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
