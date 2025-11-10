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
            provider = getattr(user, 'provider_profile', None)
            if provider:
                return ServiceRequest.objects.filter(service_type__in=provider.service_types.all(), status=ServiceRequest.STATUS_PENDING)

            return ServiceRequest.objects.filter(client=user)

        return ServiceRequest.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """Allow the client who created the service request to rate the assigned provider after completion."""
        service_request = self.get_object()
        user = request.user

        if service_request.client != user:
            return Response({'detail': 'Only the requester can rate this service.'}, status=status.HTTP_403_FORBIDDEN)

        if service_request.status != ServiceRequest.STATUS_COMPLETED:
            return Response({'detail': 'Service request must be completed before rating.'}, status=status.HTTP_400_BAD_REQUEST)

        if not service_request.provider:
            return Response({'detail': 'No provider assigned to this service request.'}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(service_request, 'rating'):
            return Response({'detail': 'This service request has already been rated.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(service_request=service_request, provider=service_request.provider, reviewer=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        """Allow a provider (authenticated user with Provider profile) to accept a pending service request.

        Conditions:
        - Request must be PENDING
        - Request must not already have a provider
        - Provider must offer the ServiceRequest.service_type
        - Provider cannot be the client
        """
        service_request = self.get_object()
        user = request.user

        provider = getattr(user, 'provider_profile', None)
        if not provider:
            return Response({'detail': 'Only providers can accept service requests.'}, status=status.HTTP_403_FORBIDDEN)

        if service_request.client == user:
            return Response({'detail': 'Client cannot accept their own request.'}, status=status.HTTP_400_BAD_REQUEST)

        if service_request.status != ServiceRequest.STATUS_PENDING:
            return Response({'detail': 'Only pending requests can be accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        if service_request.provider is not None:
            return Response({'detail': 'This service request already has a provider.'}, status=status.HTTP_400_BAD_REQUEST)

        if service_request.service_type not in provider.service_types.all():
            return Response({'detail': 'Provider does not offer this type of service.'}, status=status.HTTP_403_FORBIDDEN)

        service_request.provider = provider
        service_request.status = ServiceRequest.STATUS_IN_PROGRESS
        service_request.save()

        serializer = ServiceRequestDetailSerializer(service_request, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
