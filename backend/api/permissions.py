from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """SAFE_METHODS - всем, для прочих методов требуется авторство."""

    def has_permission(self, request, view):
        """Проверка разрешения на уровне запроса."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Проверка разрешения на уровне конкретного объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
