from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Read-only for everyone (respecting view-level auth).
    Write operations only allowed to the resource owner.
    Tries common owner attributes: user, client, owner, or compares user id to object id (for User).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return False

        # Common ownership patterns
        owner_candidates = [
            getattr(obj, "user", None),
            getattr(obj, "client", None),
            getattr(obj, "owner", None),
        ]

        if any(candidate == user for candidate in owner_candidates if candidate is not None):
            return True

        # Special case: User object itself
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            if isinstance(obj, User):
                return obj.pk == user.pk
        except Exception:
            pass

        return False

