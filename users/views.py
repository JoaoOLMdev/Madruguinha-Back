from rest_framework import viewsets, permissions
from .models import CustomUser
from .serializers import UserSerializer
from app.permissions import IsOwnerOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return CustomUser.objects.all()
        if user.is_authenticated:
            return CustomUser.objects.filter(pk=user.pk)
        return CustomUser.objects.none()