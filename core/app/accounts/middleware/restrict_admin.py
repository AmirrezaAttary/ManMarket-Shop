from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from ..models import UserType

class RestrictAdminMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated or request.user.type != UserType.superuser:
                raise Http404()
        return None