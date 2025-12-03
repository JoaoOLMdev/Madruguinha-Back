from rest_framework import serializers
from .models import ServiceRequest
from .models import Rating
from providers.serializers import ProviderSerializer
from providers.models import Provider


class RatingSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)
    provider = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'service_request', 'provider', 'reviewer', 'score', 'comment', 'created_at']
        read_only_fields = ['id', 'service_request', 'provider', 'reviewer', 'created_at']

class ServiceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    provider = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all(), required=False, allow_null=True
    )
    class Meta:
        model = ServiceRequest
        fields = ['id', 'title', 'description', 'address', 'service_type', 'provider']
        read_only_fields = ['id']
        

class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    service_type = serializers.StringRelatedField()
    provider = serializers.StringRelatedField()
    provider_id = serializers.IntegerField(source='provider.id', read_only=True)
    status = serializers.CharField()
    rating = RatingSerializer(read_only=True)

    class Meta:
        model = ServiceRequest
        fields = ['id', 'title', 'description', 'address', 'requested_date', 'completion_date', 'client', 'service_type', 'provider', 'provider_id', 'status', 'rating']
        read_only_fields = ['requested_date', 'completion_date']