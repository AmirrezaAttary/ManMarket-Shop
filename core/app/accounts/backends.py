# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import User


class EmailOrPhoneBackend(ModelBackend):
    """
    لاگین با ایمیل یا شماره موبایل (حتی اگر USERNAME_FIELD = 'id' باشد)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        user = None
        try:
            # اگر ایمیل بود
            if isinstance(username, str) and '@' in username:
                user = User.objects.get(email__iexact=username)

            # اگر شماره موبایل بود
            elif isinstance(username, str) and username.isdigit():
                user = User.objects.get(phone_number=username)

            else:
                return None

        except User.DoesNotExist:
            return None

        # بررسی پسورد و فعال بودن کاربر
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
