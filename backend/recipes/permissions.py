from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает опасные методы запроса только автору объекта,
    в остальных случаях доступ запрещен.
    """

    def has_object_permission(self, request, view, object):
        return (
            request.method in SAFE_METHODS
            or object.author == request.user
        )
