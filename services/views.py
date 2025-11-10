from rest_framework import viewsets, permissions
from .models import ServiceType
from .serializers import ServiceTypeSerializer

class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]
