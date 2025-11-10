from rest_framework import viewsets, permissions
from .models import ServiceRequest
from .serializers import ServiceRequestDetailSerializer, ServiceRequestCreateUpdateSerializer
from app.permissions import IsOwnerOrReadOnly


class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceRequestCreateUpdateSerializer
        return ServiceRequestDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return ServiceRequest.objects.all()
        if user.is_authenticated:
            return ServiceRequest.objects.filter(client=user)
        return ServiceRequest.objects.none()
