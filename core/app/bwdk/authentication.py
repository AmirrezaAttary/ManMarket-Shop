from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class OptionalJWTAuthentication(JWTAuthentication):
    """JWT auth that never blocks a public endpoint.

    The express checkout (Buy with Digikala) must work without login. A browser can still hold an
    old/expired access token in localStorage; the stock JWTAuthentication answers 401 for it even on
    an AllowAny view, which would silently force the visitor to log in. Here a bad token simply
    means "treat the request as a guest".
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (InvalidToken, TokenError):
            return None
