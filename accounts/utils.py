from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


User = get_user_model()


def get_user_from_uid(uidb64):
    """Decodes the uidb64 string and returns the matching user, or None if not found."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def get_login_data(user):
    """Returns the response data that is sent to the frontend after a successful login."""
    return {
        'detail': 'Login successful',
        'user': {'id': user.id, 'username': user.email},
    }


def get_logout_data():
    """Returns the response data that is sent to the frontend after a successful logout."""
    return {
        'detail': 'Logout successful! All tokens will be deleted. '
                  'Refresh token is now invalid.'
    }
