from django.contrib import messages
from django.shortcuts import redirect

from .permissions import role_can_access_path


class RoleAccessMiddleware:
    """
    Block department URLs when the logged-in user's role is not permitted.
    Admin may access all department routes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_allowed(request):
            messages.error(request, 'You do not have permission to access that section.')
            return redirect('core:dashboard')
        return self.get_response(request)

    def _is_allowed(self, request):
        path = request.path
        if path.startswith('/admin/'):
            return request.user.role == 'admin' or request.user.is_staff
        if path.startswith('/api/'):
            return True
        return role_can_access_path(request.user.role, path)
