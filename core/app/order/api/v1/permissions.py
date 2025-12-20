from rest_framework.permissions import BasePermission
from app.accounts.models import UserType  # مسیر ایمپورت رو بر اساس پروژه تغییر بده


class IsCustomer(BasePermission):
    """
    فقط کاربرانی که customer هستند اجازه دسترسی دارند
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.type == UserType.customer
        )
