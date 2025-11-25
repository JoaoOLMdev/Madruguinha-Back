from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Provider, ProviderApplication
from .serializers import ProviderSerializer, ProviderApplicationSerializer
from app.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            if getattr(self.request, 'user', None) and self.request.user.is_staff:
                permission_classes = [permissions.IsAdminUser]
            else:
                permission_classes = [permissions.IsAuthenticated]
        elif self.request.method in permissions.SAFE_METHODS:
            permission_classes = [permissions.AllowAny]
        else:
            from app.permissions import IsOwnerOnly

            permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Provider.objects.all()
        if user.is_authenticated:
            return Provider.objects.filter(user=user)
        return Provider.objects.all()

    def perform_create(self, serializer):
        # Prevent creating a second Provider for the same user (OneToOneField)
        user = getattr(self.request, 'user', None)
        if user is not None and hasattr(user, 'provider_profile'):
            raise ValidationError({'detail': 'User already has a provider profile.'})
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        """If the requester is staff, create Provider as before. Otherwise create a ProviderApplication for admin approval."""
        user = request.user
        if user.is_authenticated and user.is_staff:
            return super().create(request, *args, **kwargs)

        serializer = ProviderApplicationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            app = serializer.save(applicant=user)
            return Response(ProviderApplicationSerializer(app, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOnly])
    def set_active(self, request, pk=None):
        """Set provider availability (`is_active`) — owner or admin only."""
        provider = self.get_object()

        val = request.data.get('is_active')
        if val is None:
            return Response({'detail': 'Provide "is_active" boolean in body.'}, status=status.HTTP_400_BAD_REQUEST)

        # parse boolean-like values
        if isinstance(val, bool):
            is_active = val
        else:
            sval = str(val).strip().lower()
            if sval in ('1', 'true', 'yes', 'on'):
                is_active = True
            elif sval in ('0', 'false', 'no', 'off'):
                is_active = False
            else:
                return Response({'detail': 'Invalid value for is_active; use true/false.'}, status=status.HTTP_400_BAD_REQUEST)

        provider.is_active = is_active
        provider.save()
        return Response(ProviderSerializer(provider, context={'request': request}).data, status=status.HTTP_200_OK)


class ProviderApplicationViewSet(viewsets.ModelViewSet):
    """Admin viewset to review provider applications.

    Endpoints:
    - list/retrieve: admins only
    - POST /{id}/approve/: create Provider from application
    - POST /{id}/reject/: mark application rejected
    """
    queryset = ProviderApplication.objects.all()
    serializer_class = ProviderApplicationSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        app = self.get_object()
        if app.status != app.STATUS_PENDING:
            return Response({'detail': 'Application already reviewed.'}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(app.applicant, 'provider_profile'):
            return Response({'detail': 'Applicant already has a provider profile.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            provider = Provider.objects.create(user=app.applicant, description=app.description, cpf=app.cpf, is_active=True)
        except IntegrityError:
            return Response({'detail': 'Could not create provider — a provider for this user may already exist.'}, status=status.HTTP_400_BAD_REQUEST)
        if app.service_types.exists():
            provider.service_types.set(app.service_types.all())

        app.status = app.STATUS_APPROVED
        app.reviewer = request.user
        app.reviewed_at = timezone.now()
        app.save()

        return Response(ProviderSerializer(provider, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        app = self.get_object()
        if app.status != app.STATUS_PENDING:
            return Response({'detail': 'Application already reviewed.'}, status=status.HTTP_400_BAD_REQUEST)
        app.status = app.STATUS_REJECTED
        app.reviewer = request.user
        app.reviewed_at = timezone.now()
        app.save()
        return Response({'detail': 'Application rejected.'}, status=status.HTTP_200_OK)