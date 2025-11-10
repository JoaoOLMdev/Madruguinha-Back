from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ServiceRequest, Rating
from .serializers import (
    ServiceRequestDetailSerializer,
    ServiceRequestCreateUpdateSerializer,
    RatingSerializer,
)
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """Allow the client who created the service request to rate the assigned provider after completion."""
        service_request = self.get_object()
        user = request.user

        # Only the client who created the request can rate
        if service_request.client != user:
            return Response({'detail': 'Only the requester can rate this service.'}, status=status.HTTP_403_FORBIDDEN)

        # Must be completed
        if service_request.status != ServiceRequest.STATUS_COMPLETED:
            return Response({'detail': 'Service request must be completed before rating.'}, status=status.HTTP_400_BAD_REQUEST)

        # Must have an assigned provider
        if not service_request.provider:
            return Response({'detail': 'No provider assigned to this service request.'}, status=status.HTTP_400_BAD_REQUEST)

        # Can't rate twice
        if hasattr(service_request, 'rating'):
            return Response({'detail': 'This service request has already been rated.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(service_request=service_request, provider=service_request.provider, reviewer=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
