from rest_framework.permissions import BasePermission

class IsAdminOrEjecutivo(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or getattr(request.user, 'rol', None) == 'Ejecutivo'