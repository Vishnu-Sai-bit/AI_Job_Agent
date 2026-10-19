from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import request, abort, redirect, url_for, flash
from flask_login import current_user

def is_safe_redirect_url(target: str) -> bool:
    """
    Checks if a redirect target is on the same host or relative.
    Prevents open redirect attacks within internal application redirects.
    """
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

def require_ownership(resource_getter):
    """
    Decorator that fetches a resource by id from view kwargs and verifies user ownership.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource = resource_getter(*args, **kwargs)
            if not resource:
                abort(404)
            if hasattr(resource, "user_id") and resource.user_id != current_user.id:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
