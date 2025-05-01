from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardOwnerOrBoardAdmin(BasePermission):
    """
    Custom permission to allow only the board owner or a designated board admin
    to modify the board.
    """
    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS) for all.
        if request.method in SAFE_METHODS:
            return True

        # Allow if user is the board owner
        if obj.owner == request.user:
            return True

        # Allow if user is designated as a board admin
        if request.user in obj.admins.all():
            return True

        return False