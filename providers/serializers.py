from rest_framework import serializers
from .models import Provider
from services.serializers import ServiceTypeSerializer


class ProviderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    # stars should not be writable at provider creation; it's computed from ratings
    stars = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Provider
        fields = ['id', 'user', 'description', 'stars', 'cpf', 'is_active', 'service_types']