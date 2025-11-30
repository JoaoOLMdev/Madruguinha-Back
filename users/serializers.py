from rest_framework import serializers
from .models import CustomUser
from uuid import uuid4


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'password', 'email', 'phone_number', 'address', 'birth_date', 'profile_image', 'is_provider']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):

        password = validated_data.pop('password', None)

        email = validated_data.pop('email', None)

        fn = validated_data.get('first_name', '') or ''
        ln = validated_data.get('last_name', '') or ''
        base_username = (f"{fn}.{ln}".strip('.') ) if (fn or ln) else f"user{str(uuid4())[:8]}"

        username = base_username
        i = 0
        while CustomUser.objects.filter(username=username).exists():
            i += 1
            username = f"{base_username}{i}"

        user = CustomUser.objects.create_user(username=username, email=email, password=password, **validated_data)
        
        return user