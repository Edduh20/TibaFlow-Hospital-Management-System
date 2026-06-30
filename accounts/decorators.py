from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .permissions import role_can_access_app


def role_required(*roles):
    """Restrict a view to users with one of the given roles. Admin always passes."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('accounts:login')
            if user.role == 'admin' or user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return wrapper
    return decorator


def app_role_required(app_name):
    """Restrict a view based on the app_name entry in permissions.APP_ROLE_ACCESS."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('accounts:login')
            if role_can_access_app(user.role, app_name):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:dashboard')
        return wrapper
    return decorator
