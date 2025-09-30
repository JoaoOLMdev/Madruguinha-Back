from rest_framework import viewsets, permissions
from .models import ServiceRequest
from .serializers import ServiceRequestDetailSerializer, ServiceRequestCreateUpdateSerializer


class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceRequestCreateUpdateSerializer
        return ServiceRequestDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)
