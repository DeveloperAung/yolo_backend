from rest_framework.permissions import BasePermission


class IsAdminUserOnly(BasePermission):
    """
    Custom permission to allow access only to admin users.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and is an admin
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAdminOrInstructor(BasePermission):
    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated

        # Allow only admins or instructors to create or update
        return request.user.is_authenticated and request.user.role in ['admin', 'instructor']

