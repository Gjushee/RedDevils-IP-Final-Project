from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
 
 
def admin_required(view_func):
    """Only users with role='admin' on their Profile can access this view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in.')
            return redirect('register:login')
        try:
            if not request.user.profile.is_admin():
                messages.error(request, 'Access denied. Admins only.')
                return redirect('core:home')
        except Exception:
            messages.error(request, 'Access denied.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper
 
 
def red_member_required(view_func):
    """Red members, Gold members, and Admins can access this view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in.')
            return redirect('register:login')
        try:
            if not request.user.profile.is_red_or_above():
                messages.warning(request, 'This feature requires a Red membership or above.')
                return redirect('core:home')
        except Exception:
            messages.error(request, 'Access denied.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper
 
 
def gold_member_required(view_func):
    """Gold members and Admins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in.')
            return redirect('register:login')
        try:
            if not request.user.profile.is_gold_or_above():
                messages.warning(request, 'This feature requires a Gold membership.')
                return redirect('core:home')
        except Exception:
            messages.error(request, 'Access denied.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper