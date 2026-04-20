from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Extends JWT authentication to read the access token from a cookie."""

    def authenticate(self, request):
        """Tries to get the JWT from the Authorization header first, then from the cookie."""
        header = self.get_header(request)
        raw_token = self.get_raw_token(header) if header is not None else None
        if raw_token is None:
            raw_token = request.COOKIES.get(settings.ACCESS_COOKIE_NAME)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
