from rest_framework import serializers
from .models import Provider
from services.serializers import ServiceTypeSerializer


class ProviderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Provider
        fields = ['id', 'user', 'description', 'stars', 'cpf', 'is_active', 'service_types']