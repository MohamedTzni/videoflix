from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import get_user_from_uid


User = get_user_model()


def build_frontend_url(path, uid, token):
    """Builds the full frontend URL with uid and token as query parameters."""
    return f'{settings.FRONTEND_BASE_URL}{path}?uid={uid}&token={token}'


def build_uid_and_token(user):
    """Encodes the user's primary key and generates a one-time token for email links."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def send_email(subject, plain, html, recipient):
    """Sends an HTML email with plain text fallback via Django's mail backend."""
    send_mail(
        subject=subject,
        message=plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        html_message=html,
        fail_silently=False,
    )


def send_activation_email(user):
    """Sends a confirmation email with an activation link to the newly registered user."""
    uid, token = build_uid_and_token(user)
    url = build_frontend_url('/pages/auth/activate.html', uid, token)
    user_name = user.first_name or user.email
    html = render_to_string('accounts/activation_email.html', {'user_name': user_name, 'activation_url': url})
    plain = f'Dear {user_name},\n\nActivate your account:\n{url}\n\nBest regards,\nYour Videoflix Team.'
    send_email('Activate your Videoflix account', plain, html, user.email)
    return token


def send_password_reset_email(user):
    """Sends a password reset email with a one-time link to the given user."""
    uid, token = build_uid_and_token(user)
    url = build_frontend_url('/pages/auth/confirm_password.html', uid, token)
    html = render_to_string('accounts/password_reset_email.html', {'reset_url': url})
    plain = f'Hello,\n\nReset your password:\n{url}\n\nThis link is valid for 24 hours.\n\nBest regards,\nYour Videoflix team!'
    send_email('Reset your Videoflix password', plain, html, user.email)


def set_token_cookies(response, user):
    """Generates new JWT tokens for the user and stores them as HttpOnly cookies."""
    refresh = RefreshToken.for_user(user)
    set_cookie(response, settings.ACCESS_COOKIE_NAME, str(refresh.access_token))
    set_cookie(response, settings.REFRESH_COOKIE_NAME, str(refresh))


def set_cookie(response, name, value):
    """Adds a single HttpOnly cookie with the given name and value to the response."""
    response.set_cookie(
        name,
        value,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


def delete_token_cookies(response):
    """Removes both JWT cookies from the response to log the user out."""
    response.delete_cookie(settings.ACCESS_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME)


def activate_user(uidb64, token):
    """Activates the user account if the uid and token from the email link are valid."""
    user = get_user_from_uid(uidb64)
    if not user or not default_token_generator.check_token(user, token):
        return False
    user.is_active = True
    user.save(update_fields=['is_active'])
    return True


def blacklist_refresh_token(refresh_token):
    """Adds the given refresh token to the blacklist so it can no longer be used."""
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError:
        return False
    return True


def refresh_access_token(refresh_token):
    """Returns a new access token string from the given refresh token, or None if invalid."""
    try:
        refresh = RefreshToken(refresh_token)
    except TokenError:
        return None
    return str(refresh.access_token)


def send_reset_mail_if_user_exists(email):
    """Sends a password reset email only if an active account with that email exists."""
    user = User.objects.filter(email=email, is_active=True).first()
    if user:
        send_password_reset_email(user)


def change_user_password(uidb64, token, new_password, confirm_password):
    """Validates the reset link and saves the new password if everything is correct."""
    user = get_user_from_uid(uidb64)
    if not user or not default_token_generator.check_token(user, token):
        return False, 'Invalid reset link.'
    if new_password != confirm_password or not new_password:
        return False, 'Please check your inputs.'
    user.set_password(new_password)
    user.save(update_fields=['password'])
    return True, 'Your Password has been successfully reset.'
