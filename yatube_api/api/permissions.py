from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            raise MethodNotAllowed(
                {'message': "You don't have permission to access"})
        return request.method in permissions.SAFE_METHODS
