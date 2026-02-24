from rest_framework import permissions

class IsAuthorOrSupport(permissions.BasePermission):
    """
    Разрешение: только автор заявки или сотрудник поддержки/админ.
    """
    def has_object_permission(self, request, view, obj):
        user_profile = request.user.profile
        if user_profile.role in ['support', 'admin']:
            return True
        return obj.user == user_profile