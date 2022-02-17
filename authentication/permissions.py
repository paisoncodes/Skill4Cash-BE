from rest_framework.permissions import BasePermission,AllowAny,IsAuthenticated


class PostReadAllPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.is_authenticated:
                return True
