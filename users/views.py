from rest_framework import viewsets, permissions
from .models import CustomUser
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):

        if self.action == 'create':
            return [permissions.AllowAny()]
        
        else:
            permissions_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in self.permission_classes]
    