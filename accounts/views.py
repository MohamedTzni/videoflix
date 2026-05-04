from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import LoginSerializer, RegisterSerializer
from .functions import (
    activate_user,
    blacklist_refresh_token,
    change_user_password,
    delete_token_cookies,
    refresh_access_token,
    send_activation_email,
    send_reset_mail_if_user_exists,
    set_cookie,
    set_token_cookies,
)
from .utils import get_login_data, get_logout_data


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    """Creates a new user account and sends an activation email."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = send_activation_email(user)
    data = {'user': {'id': user.id, 'email': user.email}, 'token': token}
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def activate_view(request, uidb64, token):
    """Activates a user account using the uid and token from the activation email."""
    if not activate_user(uidb64, token):
        return Response({'message': 'Activation failed.'}, status=400)
    return Response({'message': 'Account successfully activated.'})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_view(request):
    """Logs the user in and sets JWT tokens as HttpOnly cookies."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    response = Response(get_login_data(user))
    set_token_cookies(response, user)
    return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def logout_view(request):
    """Logs the user out by blacklisting the refresh token and deleting all cookies."""
    refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        return Response({'detail': 'Refresh token missing.'}, status=400)
    if not blacklist_refresh_token(refresh_token):
        return Response({'detail': 'Invalid refresh token.'}, status=400)
    response = Response(get_logout_data())
    delete_token_cookies(response)
    return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def token_refresh_view(request):
    """Issues a new access token if the refresh token cookie is still valid."""
    refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        return Response({'detail': 'Refresh token missing.'}, status=400)
    access_token = refresh_access_token(refresh_token)
    if access_token is None:
        return Response({'detail': 'Invalid refresh token.'}, status=401)
    response = Response({'detail': 'Token refreshed', 'access': access_token})
    set_cookie(response, settings.ACCESS_COOKIE_NAME, access_token)
    return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def password_reset_view(request):
    """Sends a password reset email if an account with the given email exists."""
    email = request.data.get('email')
    send_reset_mail_if_user_exists(email)
    return Response({'detail': 'An email has been sent to reset your password.'})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def password_confirm_view(request, uidb64, token):
    """Sets a new password using the uid and token from the password reset email."""
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    success, message = change_user_password(uidb64, token, new_password, confirm_password)
    if not success:
        return Response({'detail': message}, status=400)
    return Response({'detail': message})
