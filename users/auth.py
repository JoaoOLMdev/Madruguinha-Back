from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer

User = get_user_model()


class EmailTokenObtainPairSerializer(serializers.Serializer):
    """Obtain JWT tokens using email + password instead of username.

    This serializer looks up the user by `email` and then authenticates
    using the user's internal `username` so the default auth backend
    continues to work.
    """

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({'detail': 'Must include "email" and "password".'})

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No active account found with the given credentials'})

        user = authenticate(username=user_obj.username, password=password)
        if user is None:
            raise serializers.ValidationError({'detail': 'No active account found with the given credentials'})
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'User is inactive'})

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class CustomTokenObtainPairSerializer(EmailTokenObtainPairSerializer):
    """
    Extends the default serializer to include full user data in the response body.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        email = attrs.get('email')
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return data

        user_data = UserSerializer(user).data
        
        data['user_id'] = user.pk
        data['email'] = user.email
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['phone_number'] = user_data.get('phone_number', '')

        return data

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer