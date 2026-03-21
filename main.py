import os
import secrets
import base64
import httpx as _httpx
from urllib.parse import urlencode
from dotenv import load_dotenv
from supabase_auth import SyncGoTrueClient
from fasthtml.common import *
from app.components import page_layout
from app.pages.catalog import DataCatalog
from app.pages.dataset import DatasetDetail
from app.pages.access import SettingsKeys, SettingsShares
from app.pages.auth import AuthPage
from app.pages.forgot_password import ForgotPasswordPage, ResetPasswordPage
from app.pages.create_org import CreateOrgPage
from app.pages.invite import InvitePage
from app.supabase_db import db_insert, db_select, db_patch, auth_invite

load_dotenv()

from app.catalog_data import seed_catalog
seed_catalog()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

class MinimalSupabase:
    def __init__(self, url, key):
        self.auth = SyncGoTrueClient(url=f"{url}/auth/v1", headers={"apikey": key, "Authorization": f"Bearer {key}"})

if supabase_url and supabase_key:
    supabase = MinimalSupabase(supabase_url, supabase_key)
else:
    print("Warning: SUPABASE_URL and SUPABASE_KEY not found in .env. Auth will fail.")
    supabase = None

APP_URL = os.environ.get("APP_URL", "https://app.opendata.london")

SNOWFLAKE_ACCOUNT = os.environ.get("SNOWFLAKE_ACCOUNT", "").lower().replace("_", "-")
SNOWFLAKE_CLIENT_ID = os.environ.get("SNOWFLAKE_CLIENT_ID", "")
SNOWFLAKE_CLIENT_SECRET = os.environ.get("SNOWFLAKE_CLIENT_SECRET", "")
SNOWFLAKE_REDIRECT_URI = f"{APP_URL}/auth/snowflake/callback"

def _sf_base_url():
    return f"https://{SNOWFLAKE_ACCOUNT}.snowflakecomputing.com"

def before(req, session):
    open_routes = ['/login', '/register', '/forgot-password', '/reset-password',
                   '/auth/google', '/auth/github', '/auth/callback',
                   '/auth/snowflake', '/auth/snowflake/callback',
                   '/invite/accept', '/invite/confirm']
    if req.url.path not in open_routes and not session.get('user'):
        return RedirectResponse('/login', status_code=303)

bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css'])

app, rt = fast_app(before=bware, secret_key=os.environ.get("SESSION_SECRET", "dev_secret_change_in_prod"))

@rt("/login", methods=["GET"])
def get_login(session):
    if session.get('user'): return RedirectResponse('/', status_code=303)
    return AuthPage(mode="login")
    
@rt("/login", methods=["POST"])
def post_login(email: str, password: str, session):
    if not supabase: return Div("Supabase not configured.", cls="error-text")
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session['user'] = email
        session['access_token'] = res.session.access_token
        return Script("window.location.href = '/';")
    except Exception as e:
        return Div(f"Login failed: {str(e)}", cls="error-text")

@rt("/register", methods=["GET"])
def get_register(session):
    if session.get('user'): return RedirectResponse('/', status_code=303)
    return AuthPage(mode="register")

@rt("/register", methods=["POST"])
def post_register(email: str, password: str, session):
    if not supabase: return Div("Supabase not configured.", cls="error-text")
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        session['user'] = email
        return Script("window.location.href = '/';")
    except Exception as e:
        if "User already registered" in str(e):
            return Div("Account already exists. Try logging in.", cls="error-text")
        return Div(f"Registration failed: {str(e)}", cls="error-text")

@rt("/logout")
def get_logout(session):
    if 'user' in session: del session['user']
    if 'access_token' in session: del session['access_token']
    if supabase:
        try: supabase.auth.sign_out()
        except: pass
    return RedirectResponse('/login', status_code=303)

# ── OAuth: Google ──
@rt("/auth/google")
def get_auth_google():
    if not supabase: return RedirectResponse('/login', status_code=303)
    result = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": f"{APP_URL}/auth/callback"}
    })
    return RedirectResponse(result.url, status_code=303)

# ── OAuth: GitHub ──
@rt("/auth/github")
def get_auth_github():
    if not supabase: return RedirectResponse('/login', status_code=303)
    result = supabase.auth.sign_in_with_oauth({
        "provider": "github",
        "options": {"redirect_to": f"{APP_URL}/auth/callback"}
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
        return RedirectResponse('/', status_code=303)
    except Exception:
        return RedirectResponse('/login?error=snowflake_failed', status_code=303)

# ── OAuth callback ──
@rt("/auth/callback")
def get_auth_callback(req, session, code: str = None):
    if not supabase or not code:
        return RedirectResponse('/login', status_code=303)
    try:
        result = supabase.auth.exchange_code_for_session({"auth_code": code})
        session['user'] = result.user.email
        session['access_token'] = result.session.access_token
        return RedirectResponse('/', status_code=303)
    except Exception as e:
        return RedirectResponse(f'/login?error=oauth_failed', status_code=303)

@rt("/forgot-password", methods=["GET"])
def get_forgot_password():
    return ForgotPasswordPage()

@rt("/forgot-password", methods=["POST"])
def post_forgot_password(email: str):
    if not supabase:
        return Div("Supabase not configured.", cls="error-text")
    try:
        supabase.auth.reset_password_for_email(email, {"redirect_to": f"{APP_URL}/reset-password"})
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
    if not supabase:
        return Div("Supabase not configured.", cls="error-text")
    try:
        supabase.auth.verify_otp({"token_hash": token, "type": "recovery"})
        supabase.auth.update_user({"password": password})
        return Div("Password updated! ", A("Sign in", href="/login"), ".", cls="success-text")
    except Exception as e:
        return Div(f"Error: {str(e)}", cls="error-text")

@rt("/create-org", methods=["GET"])
def get_create_org(session):
    if not session.get('user'): return RedirectResponse('/login', status_code=303)
    return CreateOrgPage()

@rt("/create-org", methods=["POST"])
def post_create_org(org_name: str, slug: str, session):
    if not session.get('user'):
        return Div("Not authenticated.", cls="error-text")
    if not org_name or not slug:
        return Div("Organisation name and slug are required.", cls="error-text")
    slug = slug.lower().strip().replace(" ", "-")
    try:
        # Get user ID from access token
        user = supabase.auth.get_user(session.get('access_token'))
        user_id = str(user.user.id)
        # Create org
        orgs = db_insert("organisations", {
            "name": org_name,
            "slug": slug,
            "created_by": user_id,
        })
        org_id = orgs[0]["id"]
        # Add creator as admin member
        db_insert("memberships", {
            "org_id": org_id,
            "user_id": user_id,
            "role": "admin",
            "status": "active",
        })
        return Script(f"window.location.href = '/org/{slug}';")
    except Exception as e:
        err = str(e)
        if "duplicate key" in err or "unique" in err.lower():
            return Div("That slug is already taken. Choose a different one.", cls="error-text")
        return Div(f"Error: {err}", cls="error-text")

@rt("/")
def get(session, q: str = "", category: str = ""):
    return page_layout("London Database", "/", session.get('user'), DataCatalog(category=category, q=q))

@rt("/catalog/search")
def get_catalog_search(q: str = "", category: str = ""):
    from app.pages.catalog import SearchCatalogResults
    return SearchCatalogResults(q=q, category=category)

@rt("/catalog/{slug}")
def get_dataset(slug: str, session):
    return page_layout("Dataset Details", f"/catalog/{slug}", session.get('user'), DatasetDetail(slug, session))

@rt("/catalog/{slug}/request-access", methods=["GET"])
def get_request_access(slug: str, session, type: str = "api"):
    from app.pages.request_access import RequestAccessPage
    return RequestAccessPage(slug=slug, access_type=type, session=session)

@rt("/catalog/{slug}/request-access", methods=["POST"])
def post_request_access(slug: str, access_type: str, snowflake_account: str = "", session=None):
    if not session or not session.get('user'):
        return Div("Not authenticated.", cls="error-text")
    user = supabase.auth.get_user(session.get('access_token'))
    user_id = str(user.user.id)
    try:
        if access_type == "snowflake":
            if not snowflake_account:
                return Div("Snowflake account identifier is required.", cls="error-text")
            db_insert("share_requests", {
                "user_id": user_id,
                "dataset_slug": slug,
                "snowflake_account": snowflake_account,
                "status": "pending",
            })
            return Div("Request submitted! We'll provision your Snowflake share within 24 hours.", cls="success-text")
        else:
            db_insert("dataset_access", {
                "user_id": user_id,
                "dataset_slug": slug,
                "access_type": "api",
                "status": "active",
            })
            return Script(f"window.location.href = '/keys';")
    except Exception as e:
        err = str(e)
        if "duplicate" in err.lower() or "unique" in err.lower():
            return Div("You already have access to this dataset.", cls="success-text")
        return Div(f"Error: {err}", cls="error-text")

@rt("/keys")
def get_keys(session):
    return page_layout("API Keys", "/keys", session.get('user'), SettingsKeys())

@rt("/shares")
def get_shares(session):
    return page_layout("Snowflake Shares", "/shares", session.get('user'), SettingsShares())

# Dummy routes for completeness
@rt("/queries")
def get_queries(session):
    return page_layout("Saved Queries", "/queries", session.get('user'), Div(H1("Coming Soon", style="color: white;")))
    
@rt("/settings")
def get_settings(session):
    return page_layout("Settings", "/settings", session.get('user'), Div(H1("Account Settings", style="color: white;")))

@rt("/org/{slug}")
def get_org(slug: str, session):
    from app.pages.org_dashboard import OrgDashboard
    return page_layout(f"Organisation", f"/org/{slug}", session.get('user'), OrgDashboard(slug, session))

@rt("/org/{slug}/invite", methods=["GET"])
def get_invite(slug: str, session):
    orgs = db_select("organisations", {"slug": slug})
    if not orgs: return RedirectResponse(f"/org/{slug}", status_code=303)
    return InvitePage(slug=slug, org_name=orgs[0]["name"])

@rt("/org/{slug}/invite", methods=["POST"])
def post_invite(slug: str, invited_email: str, role: str, session):
    if not session.get('user'):
        return Div("Not authenticated.", cls="error-text")
    if not invited_email:
        return Div("Email is required.", cls="error-text")
    if role not in ("admin", "member"):
        role = "member"
    try:
        orgs = db_select("organisations", {"slug": slug})
        if not orgs:
            return Div("Organisation not found.", cls="error-text")
        org_id = orgs[0]["id"]
        org_name = orgs[0]["name"]
        # Insert pending membership
        db_insert("memberships", {
            "org_id": org_id,
            "invited_email": invited_email,
            "role": role,
            "status": "pending",
        })
        # Send invite email via Supabase admin API
        auth_invite(
            email=invited_email,
            data={"org_id": org_id, "org_slug": slug, "role": role},
            redirect_to=f"{APP_URL}/invite/accept?org={slug}"
        )
        return Div(f"Invitation sent to {invited_email}.", cls="success-text")
    except Exception as e:
        err = str(e)
        if "duplicate key" in err or "unique" in err.lower():
            return Div("That person is already a member or has a pending invite.", cls="error-text")
        return Div(f"Error: {err}", cls="error-text")

@rt("/invite/accept")
def get_invite_accept(req, session, org: str = ""):
    """Landing page after clicking an invite email link.
    Supabase redirects here with access_token in the URL fragment (handled client-side).
    """
    return Html(
        Head(
            Title("Accepting Invitation | OpenData.London"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            Style("""
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { background: #0B1120; font-family: 'Inter', sans-serif; min-height: 100vh;
                       display: flex; align-items: center; justify-content: center; color: #F8FAFC; }
                .card { text-align: center; max-width: 400px; padding: 40px 20px; }
                .card h1 { font-size: 22px; font-weight: 700; margin-bottom: 10px; }
                .card p { color: #64748B; font-size: 14px; line-height: 1.6; }
            """)
        ),
        Body(
            Div(
                H1("Joining your organisation\u2026"),
                P("Please wait while we set up your access."),
                cls="card"
            ),
            Script(f"""
                const hash = window.location.hash.substring(1);
                const params = new URLSearchParams(hash);
                const token = params.get('access_token');
                const org = "{org}";
                if (token) {{
                    fetch('/invite/confirm', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{access_token: token, org: org}})
                    }}).then(r => r.json()).then(d => {{
                        if (d.ok) window.location.href = '/org/' + org;
                        else document.querySelector('p').textContent = 'Error: ' + d.error;
                    }});
                }} else {{
                    document.querySelector('p').textContent = 'Invalid or expired invite link.';
                }}
            """)
        )
    )

@rt("/invite/confirm", methods=["POST"])
async def post_invite_confirm(req, session):
    """Receives the access_token from the invite accept page, logs the user in,
    and activates their pending membership."""
    try:
        body = await req.json()
        access_token = body.get("access_token", "")
        org_slug = body.get("org", "")
        user = supabase.auth.get_user(access_token)
        user_email = user.user.email
        user_id = str(user.user.id)
        session['user'] = user_email
        session['access_token'] = access_token
        # Find pending membership by email and activate it
        orgs = db_select("organisations", {"slug": org_slug})
        if orgs:
            org_id = orgs[0]["id"]
            db_patch(
                "memberships",
                data={"user_id": user_id, "status": "active"},
                filters={"org_id": org_id, "invited_email": user_email},
            )
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@rt("/docs")
def get_docs(session):
    return page_layout("Documentation", "/docs", session.get('user'), Div(H1("API Documentation", style="color: white;")))

if __name__ == '__main__':
    # Ensure port is open, using 5002 since odl-web is likely 5001
    serve(port=5002)
