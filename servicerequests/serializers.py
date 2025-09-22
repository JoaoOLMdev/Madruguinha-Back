from rest_framework import serializers
from .models import ServiceRequest

class ServiceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = '__all__'
        

class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    provider = serializers.StringRelatedField()
    service_type = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = ServiceRequest
        fields = '__all__'