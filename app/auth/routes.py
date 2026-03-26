"""
Authentication routes: login, register, logout, OAuth, password reset.
"""
import secrets
import base64
import httpx as _httpx
from urllib.parse import urlencode
from fasthtml.common import *
from starlette.responses import Response

from app.config import (
    APP_URL,
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_CLIENT_ID,
    SNOWFLAKE_CLIENT_SECRET,
    SNOWFLAKE_REDIRECT_URI,
)
from supabase_auth.errors import AuthApiError

from app.auth.client import get_auth_client
from app.auth.middleware import get_user_id
from app.auth.password_policy import password_policy_error
from app.db.auth_admin import auth_user_exists_for_email
from app.pages.auth import AuthPage
from app.pages.forgot_password import ForgotPasswordPage, ResetPasswordPage

ENTRY_ROUTE = "/catalog"

_DUPLICATE_SIGNUP_CODES = frozenset(
    {"email_exists", "user_already_exists", "identity_already_exists"}
)


def _is_duplicate_signup_error(exc: Exception) -> bool:
    if isinstance(exc, AuthApiError) and exc.code in _DUPLICATE_SIGNUP_CODES:
        return True
    msg = str(exc).lower()
    return (
        "user already registered" in msg
        or "already been registered" in msg
        or "email address is already" in msg
    )


def _duplicate_signup_message():
    return Div(
        "This email already has an account. ",
        A("Sign in here", href="/login"),
        " to continue.",
        cls="error-text auth-alert",
        role="alert",
    )


def _signup_is_obfuscated_duplicate(res) -> bool:
    """
    GoTrue may return HTTP 200 with no session for duplicate signups (enumeration
    protection). Those payloads typically omit identities on the user object.
    """
    if res.session is not None:
        return False
    if not res.user:
        return True
    ids = res.user.identities
    if ids is None:
        return True
    return len(ids) == 0


def _sf_base_url():
    return f"https://{SNOWFLAKE_ACCOUNT}.snowflakecomputing.com"

def _to_entry_route(req=None):
    # HTMX requests should use HX-Redirect to trigger full-page navigation.
    if req and req.headers.get("HX-Request") == "true":
        return Response(status_code=200, headers={"HX-Redirect": ENTRY_ROUTE})
    return RedirectResponse(ENTRY_ROUTE, status_code=303)


def register(rt):

    @rt("/login", methods=["GET"])
    def get_login(session):
        if get_user_id(session):
            return RedirectResponse(ENTRY_ROUTE, status_code=303)
        return AuthPage(mode="login")

    @rt("/login", methods=["POST"])
    def post_login(req, email: str, password: str, session):
        policy_err = password_policy_error(password)
        if policy_err:
            return Div(policy_err, cls="error-text")
        supabase = get_auth_client()
        if not supabase:
            return Div("Supabase not configured.", cls="error-text")
        try:
            res = supabase.sign_in_with_password({"email": email, "password": password})
            session['user'] = email
            session['access_token'] = res.session.access_token
            return _to_entry_route(req)
        except Exception as e:
            return Div(f"Login failed: {str(e)}", cls="error-text")

    @rt("/signup", methods=["GET"])
    def get_signup_redirect():
        return RedirectResponse("/register", status_code=302)

    @rt("/register", methods=["GET"])
    def get_register(session):
        if get_user_id(session):
            return RedirectResponse(ENTRY_ROUTE, status_code=303)
        return AuthPage(mode="register")

    @rt("/register", methods=["POST"])
    def post_register(req, email: str, password: str, session):
        policy_err = password_policy_error(password)
        if policy_err:
            return Div(policy_err, cls="error-text")
        email_norm = email.strip().lower()
        if auth_user_exists_for_email(email_norm):
            return _duplicate_signup_message()
        supabase = get_auth_client()
        if not supabase:
            return Div("Supabase not configured.", cls="error-text")
        try:
            res = supabase.sign_up({"email": email_norm, "password": password})
            if res.session:
                session['user'] = email_norm
                session['access_token'] = res.session.access_token
                return _to_entry_route(req)
            if _signup_is_obfuscated_duplicate(res):
                return _duplicate_signup_message()
            return Div(
                "Check your email to confirm your account before signing in.",
                cls="success-text",
            )
        except Exception as e:
            if _is_duplicate_signup_error(e):
                return _duplicate_signup_message()
            return Div(f"Registration failed: {str(e)}", cls="error-text")

    @rt("/signup", methods=["POST"])
    def post_signup(req, email: str, password: str, session):
        return post_register(req=req, email=email, password=password, session=session)

    @rt("/logout")
    def get_logout(session):
        if 'user' in session:
            del session['user']
        if 'access_token' in session:
            del session['access_token']
        supabase = get_auth_client()
        if supabase:
            try:
                supabase.sign_out()
            except Exception:
                pass
        return RedirectResponse('/login', status_code=303)

    # ── OAuth: Google ──
    @rt("/auth/google")
    def get_auth_google():
        supabase = get_auth_client()
        if not supabase:
            return RedirectResponse('/login', status_code=303)
        result = supabase.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": f"{APP_URL}/auth/callback"},
        })
        return RedirectResponse(result.url, status_code=303)

    # ── OAuth: GitHub ──
    @rt("/auth/github")
    def get_auth_github():
        supabase = get_auth_client()
        if not supabase:
            return RedirectResponse('/login', status_code=303)
        result = supabase.sign_in_with_oauth({
            "provider": "github",
            "options": {"redirect_to": f"{APP_URL}/auth/callback"},
        })
        return RedirectResponse(result.url, status_code=303)

    # ── OAuth: Snowflake ──
    @rt("/auth/snowflake")
    def get_auth_snowflake(session):
        if not SNOWFLAKE_CLIENT_ID:
            return RedirectResponse('/login', status_code=303)
        state = secrets.token_urlsafe(16)
        session['sf_state'] = state
        qs = urlencode({
            "client_id": SNOWFLAKE_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": SNOWFLAKE_REDIRECT_URI,
            "state": state,
            "scope": "session:role:PUBLIC",
        })
        return RedirectResponse(f"{_sf_base_url()}/oauth/authorize?{qs}", status_code=303)

    @rt("/auth/snowflake/callback")
    def get_auth_snowflake_callback(req, session, code: str = None, state: str = None, error: str = None):
        if error or not code:
            return RedirectResponse('/login?error=snowflake_denied', status_code=303)
        if state != session.get('sf_state'):
            return RedirectResponse('/login?error=invalid_state', status_code=303)
        session.pop('sf_state', None)
        try:
            credentials = base64.b64encode(
                f"{SNOWFLAKE_CLIENT_ID}:{SNOWFLAKE_CLIENT_SECRET}".encode()
            ).decode()
            r = _httpx.post(
                f"{_sf_base_url()}/oauth/token-request",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": SNOWFLAKE_REDIRECT_URI,
                },
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            r.raise_for_status()
            token_data = r.json()
            username = token_data.get("username", "")
            access_token = token_data.get("access_token", "")
            if not username:
                return RedirectResponse('/login?error=snowflake_no_user', status_code=303)
            session['user'] = f"{username}@snowflake"
            session['access_token'] = access_token
            session['auth_provider'] = 'snowflake'
            return RedirectResponse(ENTRY_ROUTE, status_code=303)
        except Exception:
            return RedirectResponse('/login?error=snowflake_failed', status_code=303)

    # ── OAuth callback ──
    @rt("/auth/callback")
    def get_auth_callback(req, session, code: str = None):
        supabase = get_auth_client()
        if not supabase or not code:
            return RedirectResponse('/login', status_code=303)
        try:
            result = supabase.exchange_code_for_session({"auth_code": code})
            session['user'] = result.user.email
            session['access_token'] = result.session.access_token
            return RedirectResponse(ENTRY_ROUTE, status_code=303)
        except Exception:
            return RedirectResponse('/login?error=oauth_failed', status_code=303)

    # ── Password reset ──
    @rt("/forgot-password", methods=["GET"])
    def get_forgot_password():
        return ForgotPasswordPage()

    @rt("/forgot-password", methods=["POST"])
    def post_forgot_password(email: str):
        supabase = get_auth_client()
        if not supabase:
            return Div("Supabase not configured.", cls="error-text")
        try:
            supabase.reset_password_for_email(email, {"redirect_to": f"{APP_URL}/reset-password"})
            return Div("Check your email for a password reset link.", cls="success-text")
        except Exception as e:
            return Div(f"Error: {str(e)}", cls="error-text")

    @rt("/reset-password", methods=["GET"])
    def get_reset_password(req):
        token = req.query_params.get("token", "")
        return ResetPasswordPage(token=token)

    @rt("/reset-password", methods=["POST"])
    def post_reset_password(token: str, password: str, confirm_password: str):
        if password != confirm_password:
            return Div("Passwords do not match.", cls="error-text")
        policy_err = password_policy_error(password)
        if policy_err:
            return Div(policy_err, cls="error-text")
        supabase = get_auth_client()
        if not supabase:
            return Div("Supabase not configured.", cls="error-text")
        try:
            supabase.verify_otp({"token_hash": token, "type": "recovery"})
            supabase.update_user({"password": password})
            return Div("Password updated! ", A("Sign in", href="/login"), ".", cls="success-text")
        except Exception as e:
            return Div(f"Error: {str(e)}", cls="error-text")
