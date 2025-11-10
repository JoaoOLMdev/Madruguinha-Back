from rest_framework import viewsets, permissions
from .models import Provider
from .serializers import ProviderSerializer
from app.permissions import IsOwnerOrReadOnly

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAdminUser]
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
        serializer.save(user=self.request.user)