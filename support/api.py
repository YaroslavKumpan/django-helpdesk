from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions

from .permissions import IsAuthorOrSupport
from .models import SupportRequest
from .serializers import UserRegistrationSerializer, UserLoginSerializer, SupportRequestSerializer, \
    SupportMessageSerializer


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Пользователь успешно зарегистрирован!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupportRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SupportRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrSupport]

    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        if profile.role in ["support", "admin"]:
            return SupportRequest.objects.all()
        return SupportRequest.objects.filter(user=profile)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def update(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.role not in ['support', 'admin']:
            instance = self.get_object()
            if 'status' in request.data and request.data['status'] != instance.status:
                raise PermissionDenied("Вы не можете изменять статус заявки.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.role not in ['support', 'admin']:
            instance = self.get_object()
            if 'status' in request.data and request.data['status'] != instance.status:
                raise PermissionDenied("Вы не можете изменять статус заявки.")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.role != 'admin':
            raise PermissionDenied("Только администратор может удалять заявки.")
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["post"],
        serializer_class=SupportMessageSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def messages(self, request, pk=None):
        """
        Эндпоинт для создания сообщения в заявке.
        POST /api/requests/{id}/messages/
        """
        support_request = self.get_object()
        data = request.data.copy()
        data["support_request"] = support_request.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
