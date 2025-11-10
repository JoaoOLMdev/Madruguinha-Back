from rest_framework import serializers
from .models import ServiceRequest

class ServiceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ['id', 'title', 'description', 'address', 'service_type']
        read_only_fields = ['id']
        

class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    service_type = serializers.StringRelatedField()

    class Meta:
        model = ServiceRequest
        fields = ['id', 'title', 'description', 'address', 'requested_date', 'client', 'service_type']