from rest_framework import viewsets, permissions
from .models import Provider
from .serializers import ProviderSerializer
from app.permissions import IsOwnerOrReadOnly

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Provider.objects.all()
        if user.is_authenticated:
            return Provider.objects.filter(user=user)
        return Provider.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)