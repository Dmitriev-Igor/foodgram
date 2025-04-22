from rest_framework.permissions import SAFE_METHODS, BasePermission


class AnonimOrAuthenticatedReadOnly(BasePermission):
    """
    Разрешает анонимному или авторизованному пользователю
    только безопасные запросы.
    """

    def has_permission(self, request, view):
        return (
            (request.method in SAFE_METHODS
             and (request.user.is_anonymous
                  or request.user.is_authenticated))
            or request.user.is_superuser
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, object):
        return (
            (request.method in SAFE_METHODS
             and (request.user.is_anonymous
                  or request.user.is_authenticated))
            or request.user.is_superuser
            or request.user.is_staff
        )


class AuthorOrReadOnly(BasePermission):
    """
    Разрешает опасные методы запроса только автору объекта,
    в остальных случаях доступ запрещен.
    """

    def has_object_permission(self, request, view, object):
        return (
            request.method in SAFE_METHODS
            or object.author == request.user
        )
