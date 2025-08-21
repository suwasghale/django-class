from django.shortcuts import redirect
from django.views.decorators.cache import cache_control

def admin_only(view_function):
    """
    Restrict access to admin (staff) users only.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_function(request, *args, **kwargs)
        return redirect('/')  # Redirect non-admin users to home
    return _wrapped_view


def redirect_if_logged_in(view_function):
    """
    Redirect authenticated users away from login/register pages.
    Also disables caching so the browser back button won't show old login page.
    """
    @cache_control(no_cache=True, must_revalidate=True, no_store=True)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile_view')  # Change this to your dashboard/profile URL
        return view_function(request, *args, **kwargs)
    return _wrapped_view
