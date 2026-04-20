from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Validates the registration data and creates a new inactive user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        """Checks that passwords match and the email is not already registered."""
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError('Please check your inputs.')
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError('Please check your inputs.')
        return attrs

    def create(self, validated_data):
        """Creates the user with is_active=False so they must activate via email first."""
        validated_data.pop('confirmed_password')
        return User.objects.create_user(is_active=False, **validated_data)


class LoginSerializer(serializers.Serializer):
    """Validates the login credentials and returns the authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Checks that the credentials are correct and the account is active."""
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if user is None or not user.is_active:
            raise serializers.ValidationError('Please check your inputs.')
        attrs['user'] = user
        return attrs
