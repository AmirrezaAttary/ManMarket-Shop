from rest_framework.permissions import BasePermission
from app.accounts.models import UserType  # مسیر ایمپورت رو بر اساس پروژه تغییر بده

class IsAdminOrSuperUser(BasePermission):
    """
    فقط کاربرانی که admin یا superuser هستند اجازه دسترسی دارند
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.type in [UserType.admin, UserType.superuser]
        )