from rest_framework import viewsets, permissions
from .models import ServiceType
from .serializers import ServiceTypeSerializer

class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
