from rest_framework import serializers
from .models import Provider
from services.serializers import ServiceTypeSerializer
from services.models import ServiceType


class ProviderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    user_address = serializers.CharField(source='user.address', read_only=True)
    provider_image = serializers.ImageField(source='image', required=False, allow_null=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    service_types_ids = serializers.PrimaryKeyRelatedField(queryset=ServiceType.objects.all(), many=True, required=False)
    stars = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Provider
        fields = ['id', 'user', 'nickname', 'user_phone', 'user_address', 'provider_image', 'description', 'stars', 'cpf_cnpj', 'is_active', 'service_types', 'service_types_ids']

    def create(self, validated_data):
        service_types = validated_data.pop('service_types_ids', None)
        instance = super().create(validated_data)
        if service_types:
            instance.service_types.set(service_types)
        return instance

    def update(self, instance, validated_data):
        service_types = validated_data.pop('service_types_ids', None)
        instance = super().update(instance, validated_data)
        if service_types is not None:
            instance.service_types.set(service_types)
        return instance


class ProviderApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True) 
    service_types_ids = serializers.PrimaryKeyRelatedField(queryset=ServiceType.objects.all(), many=True, required=False)

    class Meta:
        model = getattr(__import__('providers.models', fromlist=['ProviderApplication']), 'ProviderApplication')
        fields = ['id', 'applicant', 'description', 'cpf_cnpj', 'service_types', 'service_types_ids', 'status', 'created_at', 'reviewed_at', 'reviewer']
        read_only_fields = ['id', 'applicant', 'status', 'created_at', 'reviewed_at', 'reviewer']

    def create(self, validated_data):
        service_types = validated_data.pop('service_types_ids', None)
        instance = super().create(validated_data)
        if service_types:
            instance.service_types.set(service_types)
        return instance