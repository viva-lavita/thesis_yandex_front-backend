from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.id == request.user.id or request.user.is_staff


class NotIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsStuffOrReadOnly(BasePermission):
    """Админ или только чтение."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff
