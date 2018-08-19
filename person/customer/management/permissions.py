from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False

        # Check if the user owns the account
        authenticated_user_id = request.user.identifier
        authenticated_user = request.user

        if authenticated_user.is_active \
                and obj.identifier == authenticated_user_id \
                or request.user.is_staff:
            return True
        else:
            return False
