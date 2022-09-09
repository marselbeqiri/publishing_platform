from django.http import Http404
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from applications.authentication.models import User
from applications.authentication.serializers import RegistrationSerializer, UserInfoSerializer


class UserCRUDPermission(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return bool(request.user and request.user.is_authenticated)


class UserAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = (UserCRUDPermission,)

    def get_object(self):
        user = self.request.user
        if not user.id:
            raise Http404

        return user

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RegistrationSerializer
        return super().get_serializer_class()

    def get_exception_handler_context(self):
        super_context = super().get_exception_handler_context()
        super_context['password_action'] = True
        return super_context


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """

    class ChangePasswordSerializer(serializers.Serializer):
        old_password = serializers.CharField(required=True)
        new_password = serializers.CharField(required=True)

    serializer_class = ChangePasswordSerializer

    def get_object(self):
        user = self.request.user
        if not user.id:
            raise Http404

        return user

    def perform_update(self, serializer):
        user: User = self.get_object()
        if not user.check_password(serializer.data.get("old_password")):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.validate_password(serializer.data.get("new_password"))
        user.set_password(serializer.data.get("new_password"))
        user.save()
        response = {
            'status': 'success',
            'code': status.HTTP_200_OK,
            'message': 'Password updated successfully',
        }

        return Response(response)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.perform_update(serializer)

    def get_exception_handler_context(self):
        super_context = super().get_exception_handler_context()
        super_context['password_action'] = True
        return super_context


user_view = UserAPIView.as_view()
change_password_view = ChangePasswordView.as_view()
