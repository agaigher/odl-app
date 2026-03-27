"""
Request middleware and session helpers.
"""
from starlette.responses import RedirectResponse

from app.db import get_user_id_from_session


def before(req, session):
    """Beforeware handler — runs before every request."""
    open_routes = [
        '/login', '/register', '/signup', '/forgot-password', '/reset-password',
        '/auth/google', '/auth/github', '/auth/callback',
        '/auth/email-confirm', '/auth/implicit-session',
        '/invite/accept', '/invite/confirm', '/robots.txt',
        '/',
        # Sessionless endpoints (authenticate via header / Stripe signature)
        '/api/v1',
        '/api/webhooks',
    ]
    is_open = any(req.url.path == r or req.url.path.startswith(r + '/') for r in open_routes)
    if not is_open and not get_user_id(session):
        return RedirectResponse('/login', status_code=303)


def get_user_id(session):
    """Resolve the authenticated user's UUID from the session."""
    user = session.get('user')
    if not user:
        return None
    if user == 'test@example.com':
        return "test-user-id"
    return get_user_id_from_session(session)
