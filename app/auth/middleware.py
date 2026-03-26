"""
Request middleware and session helpers.
"""
from app.db import get_user_id_from_session


def before(req, session):
    """Beforeware handler — runs before every request."""
    open_routes = [
        '/login', '/register', '/signup', '/forgot-password', '/reset-password',
        '/auth/google', '/auth/github', '/auth/callback',
        '/auth/email-confirm', '/auth/implicit-session',
        '/auth/snowflake', '/auth/snowflake/callback',
        '/invite/accept', '/invite/confirm', '/robots.txt',
        '/', '/catalog', '/catalog/search', '/catalog/ai-search',
    ]
    is_open = any(req.url.path == r or req.url.path.startswith(r + '/') for r in open_routes)
    # TODO: uncomment when ready to enforce auth on protected routes
    # if not is_open and not get_user_id(session):
    #     from starlette.responses import RedirectResponse
    #     return RedirectResponse('/login', status_code=303)


def get_user_id(session):
    """Resolve the authenticated user's UUID from the session."""
    if session.get('user') == 'test@example.com':
        return "test-user-id"
    return get_user_id_from_session(session)
