from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import CustomUser
from .serializers import UserSerializer
from app.permissions import IsOwnerOrReadOnly


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
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


    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def service_requests(self, request, pk=None):
        """List all service requests made by this user."""
        from servicerequests.models import ServiceRequest
        from servicerequests.serializers import ServiceRequestDetailSerializer
        user = self.get_object()
        requests = ServiceRequest.objects.filter(client=user)
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = ServiceRequestDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ServiceRequestDetailSerializer(requests, many=True, context={'request': request})
        return Response(serializer.data)
    
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request, pk=None):
        """
        Change password for the user. Expects JSON:
        { "current_password": "...", "new_password": "..." }
        """
        user = self.get_object()

        if request.user.pk != user.pk and not request.user.is_staff:
            return Response({'detail': 'Não autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({'detail': 'Campos faltando.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'detail': 'Senha atual incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)