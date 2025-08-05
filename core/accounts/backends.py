from django.contrib.auth.backends import ModelBackend
from accounts.models import User

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        user = None
        try:
            if '@' in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(phone_number=username)
        except User.DoesNotExist:
            print(f"User with username {username} not found.")
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            print(f"User {user} authenticated successfully.")
            return user

        print(f"Password check failed for user {user}.")
        return None
