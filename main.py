import os
import secrets
import base64
import httpx as _httpx
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()
from supabase_auth import SyncGoTrueClient
from fasthtml.common import *
from app.components import page_layout
from app.pages.catalog import DataCatalog
from app.pages.dashboard import Dashboard
from app.pages.dataset import DatasetDetail
from app.pages.access import SettingsKeys, SettingsShares
from app.pages.auth import AuthPage
from app.pages.forgot_password import ForgotPasswordPage, ResetPasswordPage
from app.pages.create_org import CreateOrgPage
from app.pages.invite import InvitePage
from app.pages.organisations import OrganisationsPage
from app.supabase_db import db_insert, db_select, db_patch, db_delete, auth_invite, log_audit, get_user_id_from_session
from app.email import send_org_invite


from app.catalog_data import seed_catalog
seed_catalog()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

class MinimalSupabase:
    def __init__(self, url, key):
        self.auth = SyncGoTrueClient(url=f"{url}/auth/v1", headers={"apikey": key, "Authorization": f"Bearer {key}"})
    
    def table(self, table_name):
        from app.supabase_db import db_patch, db_delete, db_insert
        class TableHelper:
            def __init__(self, t):
                self.t = t
                self.filters = {}
            def update(self, data):
                self.data = data
                return self
            def insert(self, data):
                self.data = data
                self.action = "insert"
                return self
            def eq(self, col, val):
                self.filters[col] = val
                return self
            def delete(self):
                self.action = "delete"
                return self
            def upsert(self, data):
                db_insert(self.t, data)
                return self
            def execute(self):
                from app.supabase_db import db_patch, db_delete, db_insert
                class Res:
                    def __init__(self, data=None): self.data = data
                
                if hasattr(self, 'action') and self.action == "insert":
                    d = db_insert(self.t, self.data)
                    return Res(d)
                elif hasattr(self, 'data'):
                    db_patch(self.t, self.data, self.filters)
                    return Res(self.data)
                elif hasattr(self, 'action') and self.action == "delete":
                    db_delete(self.t, self.filters)
                    return Res([])
                return Res([])
        return TableHelper(table_name)

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
                   '/invite/accept', '/invite/confirm', '/robots.txt',
                   '/', '/catalog', '/catalog/search', '/catalog/ai-search']
    
    # Check if route starts with open routes if it's dynamic
    is_open = any(req.url.path == r or req.url.path.startswith(r + '/') for r in open_routes)
    
    if not is_open and not session.get('user'):
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
        if res.session:
            session['access_token'] = res.session.access_token
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
    user_id = _get_user_id(session)
    if not user_id:
        return Div("Not authenticated.", cls="error-text")
    if not org_name or not slug:
        return Div("Organisation name and slug are required.", cls="error-text")
    
    slug = slug.lower().strip().replace(" ", "-")
    try:
        # Create org
        orgs = db_insert("organisations", {
            "name": org_name,
            "slug": slug,
            "created_by": user_id,
        })
        if not orgs: raise Exception("Failed to create organisation record.")
        org_id = orgs[0]["id"]
        
        # Add creator as owner member
        db_insert("memberships", {
            "org_id": org_id,
            "user_id": user_id,
            "role": "owner",
            "status": "active",
        })
        
        # Set as active org
        session['active_org_id'] = org_id
        session['force_header_refresh'] = True
        log_audit(org_id, user_id, "Organization created", "organisation", org_id)
        
        return Script("window.location.href = '/projects';")
    except Exception as e:
        err = str(e)
        if "duplicate key" in err or "unique" in err.lower():
            return Div("That slug is already taken. Choose a different one.", cls="error-text")
        return Div(f"Error: {err}", cls="error-text")

def _get_user_id(session):
    return get_user_id_from_session(session)


@rt("/")
def get(session):
    return RedirectResponse('/dashboard', status_code=303)

@rt("/dashboard")
def get_dashboard(session):
    user_email = session.get('user', '')
    try:
        user = supabase.auth.get_user(session.get('access_token'))
        user_id = str(user.user.id)
    except Exception:
        user_id = ""
    return page_layout("Dashboard", "/dashboard", user_email, Dashboard(user_id=user_id, user_email=user_email), session=session)

@rt("/catalog")
def get_catalog(session, q: str = "", category: str = "", access: str = "", freq: str = "", page: int = 1, per_page: int = 25):
    user_id = _get_user_id(session)
    return page_layout("London Database", "/catalog", session.get('user'),
                       DataCatalog(category=category, q=q, user_id=user_id,
                                   access_filter=access, freq_filter=freq,
                                   page=page, per_page=per_page), session=session)

@rt("/catalog/search")
def get_catalog_search(session, q: str = "", category: str = "", access: str = "", freq: str = "", page: int = 1, per_page: int = 25):
    from app.pages.catalog import SearchCatalogResults
    user_id = _get_user_id(session)
    return SearchCatalogResults(q=q, category=category, user_id=user_id,
                                access_filter=access, freq_filter=freq,
                                page=page, per_page=per_page)

@rt("/catalog/ai-search", methods=["POST"])
def post_ai_search(session, query: str = ""):
    from app.pages.catalog import AiSearchResults
    user_id = _get_user_id(session)
    return AiSearchResults(query=query, user_id=user_id)

@rt("/catalog/{slug}/integration-modal", methods=["GET"])
def get_integration_modal(slug: str, session):
    from app.pages.catalog import IntegrationModal
    user_id = _get_user_id(session)
    if not user_id: return Script("window.location.href='/login'")
    
    project_id = session.get('active_project_id')
    if not project_id:
        return Div("Please select or create an active Project from the Projects tab before managing integrations.", cls="error-text", style="padding:24px;background:#fff;border-radius:8px;")

    try:
        ds = db_select("datasets", {"slug": slug})
        title = ds[0].get("title") if ds else slug
    except Exception:
        title = slug
    return IntegrationModal(slug, title, project_id)

@rt("/catalog/{slug}/add-btn", methods=["GET"])
def get_add_btn(slug: str, session):
    from app.pages.catalog import _add_btn
    user_id = _get_user_id(session)
    if not user_id: return _add_btn(slug, False)
    
    project_id = session.get('active_project_id')
    if not project_id: return _add_btn(slug, False)

    try:
        project_ints = db_select("integrations", {"project_id": project_id})
        project_int_ids = {i["id"] for i in project_ints}
        
        items = db_select("dataset_integrations", {"dataset_slug": slug})
        is_assigned = any(item["integration_id"] in project_int_ids for item in items)
        return _add_btn(slug, is_assigned)
    except Exception:
        return _add_btn(slug, False)

@rt("/integrations/{int_id}/toggle", methods=["POST"])
def post_toggle_integration(int_id: str, slug: str, session):
    from app.pages.catalog import _int_checkbox
    user_id = _get_user_id(session)
    if not user_id: return ""
    try:
        existing = db_select("dataset_integrations", {"integration_id": int_id, "user_id": user_id, "dataset_slug": slug})
        if existing:
            db_delete("dataset_integrations", {"integration_id": int_id, "user_id": user_id, "dataset_slug": slug})
            in_list = False
        else:
            db_insert("dataset_integrations", {"integration_id": int_id, "user_id": user_id, "dataset_slug": slug})
            in_list = True
        ints = db_select("user_integrations", {"id": int_id, "user_id": user_id})
        int_name = ints[0]["name"] if ints else "Integration"
        return _int_checkbox(int_id, slug, in_list, int_name)
    except Exception:
        return ""

@rt("/catalog/{slug}/favourite-modal", methods=["GET"])
def get_favourite_modal(slug: str, session):
    from app.pages.catalog import FavouriteModal
    user_id = _get_user_id(session)
    if not user_id:
        return Script("window.location.href='/login'")
    try:
        ds = db_select("datasets", {"slug": slug})
        title = ds[0].get("title") if ds else slug
    except Exception:
        title = slug
    return FavouriteModal(slug, title, user_id)

@rt("/catalog/{slug}/fav-btn", methods=["GET"])
def get_fav_btn(slug: str, session):
    from app.pages.catalog import _fav_btn
    user_id = _get_user_id(session)
    if not user_id: return _fav_btn(slug, False)
    try:
        items = db_select("favourite_items", {"user_id": user_id, "dataset_slug": slug})
        return _fav_btn(slug, len(items) > 0)
    except Exception:
        return _fav_btn(slug, False)

@rt("/favourite-lists", methods=["POST"])
def post_favourite_lists(slug: str, name: str, session):
    from app.pages.catalog import _list_checkbox
    user_id = _get_user_id(session)
    if not user_id or not name.strip(): return ""
    try:
        created = db_insert("favourite_lists", {"user_id": user_id, "name": name.strip()})
        list_id = created[0]["id"]
        db_insert("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
        return _list_checkbox(list_id, slug, True, name.strip())
    except Exception:
        return ""

@rt("/favourite-lists/{list_id}/toggle", methods=["POST"])
def post_toggle_list_item(list_id: str, slug: str, session):
    from app.pages.catalog import _list_checkbox
    user_id = _get_user_id(session)
    if not user_id: return ""
    try:
        existing = db_select("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
        if existing:
            db_delete("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
            in_list = False
        else:
            db_insert("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
            in_list = True
        lst = db_select("favourite_lists", {"id": list_id, "user_id": user_id})
        list_name = lst[0]["name"] if lst else "List"
        return _list_checkbox(list_id, slug, in_list, list_name)
    except Exception:
        return ""

@rt("/favourite-lists/create", methods=["POST"])
def post_create_fav_list(name: str, session):
    user_id = _get_user_id(session)
    if user_id and name.strip():
        try:
            db_insert("favourite_lists", {"user_id": user_id, "name": name.strip()})
            return "ok"
        except Exception:
            return "error"
    return "unauthorized"

@rt("/favourite-lists/{list_id}/items/{slug}/remove", methods=["POST"])
def post_remove_fav_item(list_id: str, slug: str, session):
    user_id = _get_user_id(session)
    if user_id:
        try:
            db_delete("favourite_items", {"list_id": list_id, "dataset_slug": slug, "user_id": user_id})
        except Exception:
            pass
    return RedirectResponse("/favourites", status_code=303)

@rt("/favourite-lists/{list_id}/delete", methods=["POST"])
def post_delete_fav_list(list_id: str, session):
    user_id = _get_user_id(session)
    if user_id:
        try:
            db_delete("favourite_items", {"list_id": list_id, "user_id": user_id})
            db_delete("favourite_lists", {"id": list_id, "user_id": user_id})
        except Exception:
            pass
    return RedirectResponse("/favourites", status_code=303)

@rt("/favourites")
def get_favourites(session):
    from app.pages.catalog import FavouritesView
    user_id = _get_user_id(session)
    return page_layout("Favourites", "/favourites", session.get('user'), FavouritesView(user_id=user_id), session=session)

@rt("/catalog/{slug}")
def get_dataset(slug: str, session):
    return page_layout("Dataset Details", f"/catalog/{slug}", session.get('user'), DatasetDetail(slug, session), session=session)

@rt("/catalog/{slug}/request-access", methods=["GET"])
def get_request_access(slug: str, session, type: str = "api"):
    from app.pages.request_access import RequestAccessPage
    return RequestAccessPage(slug=slug, access_type=type, session=session)

@rt("/catalog/{slug}/request-access", methods=["POST"])
def post_request_access(slug: str, access_type: str, snowflake_account: str = "", session=None):
    if not session or not session.get('user'):
        return Div("Not authenticated.", cls="error-text")
    try:
        user = supabase.auth.get_user(session.get('access_token'))
        user_id = str(user.user.id)
    except Exception:
        return Div("Authentication error. Please log in again.", cls="error-text")
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

@rt("/integrations")
def get_integrations(session):
    from app.pages.integrations import IntegrationsView
    user_id = _get_user_id(session)
    return page_layout("Data Integrations", "/integrations", session.get('user'), IntegrationsView(user_id=user_id, session=session))

@rt("/integrations/create", methods=["POST"])
def post_create_integration(name: str, type: str, session):
    from app.pages.integrations import _integration_row
    user_id = _get_user_id(session)
    project_id = session.get('active_project_id')
    if user_id and project_id and name.strip() and type in ("api", "snowflake"):
        try:
            created = db_insert("integrations", {
                "project_id": project_id, 
                "name": name.strip(),
                "type": type
            })
            if created:
                log_audit(session.get('active_org_id'), user_id, f"Created integration '{name}'", "integration", created[0]["id"])
                return _integration_row(created[0])
        except Exception:
            pass
    return ""

@rt("/integrations/{int_id}/delete", methods=["POST"])
def post_delete_integration(int_id: str, session):
    user_id = _get_user_id(session)
    if user_id:
        try:
            db_delete("integrations", {"id": int_id})
            log_audit(session.get('active_org_id'), user_id, f"Deleted integration {int_id}", "integration", int_id)
        except Exception:
            pass
    return ""

@rt("/integrations/{int_id}")
def get_integration_detail(int_id: str, session):
    from app.pages.integration_detail import IntegrationDetailView
    user_id = _get_user_id(session)
    if not user_id: return RedirectResponse("/login")
    return page_layout("Integration Details", "/integrations", session.get('user'), IntegrationDetailView(integration_id=int_id, user_id=user_id, session=session))

@rt("/integrations/{int_id}/remove-dataset/{slug}", methods=["POST"])
def post_int_remove_dataset(int_id: str, slug: str, session):
    user_id = _get_user_id(session)
    if user_id:
        try: db_delete("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
        except: pass
    return ""

@rt("/integrations/{int_id}/toggle", methods=["POST"])
def post_toggle_integration(int_id: str, slug: str, session):
    user_id = _get_user_id(session)
    if not user_id: return ""
    try:
        existing = db_select("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
        if existing:
            db_delete("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
            in_list = False
        else:
            db_insert("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
            in_list = True
        
        ints = db_select("integrations", {"id": int_id})
        int_name = ints[0]["name"] if ints else "Integration"
        
        from app.pages.catalog import _int_checkbox
        return _int_checkbox(int_id, slug, in_list, int_name)
    except Exception:
        return ""

# Dummy routes for completeness
@rt("/queries")
def get_queries(session):
    return page_layout("SQL Queries", "/queries", session.get('user'), Div(H1("Coming Soon", style="color: white;")), session=session)
    
@rt("/settings")
def get_settings(req, session, tab: str = 'general'):
    from app.pages.settings import OrganizationSettings
    user_id = _get_user_id(session)
    if not user_id: return RedirectResponse("/login", status_code=303)
    
    content = OrganizationSettings(user_id, session, tab)
    if "HX-Request" in req.headers: return content
    return page_layout("Organization Settings", "/settings", session.get('user'), content, session=session, full_width=True)

@rt("/billing")
def get_billing(session):
    from app.pages.billing import BillingDashboard
    user_id = _get_user_id(session)
    if not user_id: return RedirectResponse("/login", status_code=303)
    return page_layout("Billing", "/billing", session.get('user'), BillingDashboard(user_id=user_id, session=session))

import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_dummy")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_dummy")

@rt("/billing/checkout", methods=["POST"])
def post_billing_checkout(req, session, package: str):
    user_id = _get_user_id(session)
    if not user_id: return RedirectResponse("/login", status_code=303)
    
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        org_id = memberships[0]["org_id"] if memberships else None
        
        billing_email = None
        if org_id:
            org_rows = db_select("organisations", {"id": org_id})
            if org_rows:
                billing_email = org_rows[0].get("billing_email")
    except:
        org_id = None
        
    if not org_id:
        return Div("Organization not found", cls="error-text")
        
    domain = str(req.base_url).rstrip("/")
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': '10,000 Data Credits',
                        'description': 'Prepaid compute and API querying credits for OpenData.London'
                    },
                    'unit_amount': 1000,
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={
                'org_id': org_id,
                'credits_to_add': 10000
            },
            customer_email=billing_email if billing_email else None,
            success_url=f"{domain}/billing?success=true",
            cancel_url=f"{domain}/billing?canceled=true",
        )
        return RedirectResponse(checkout_session.url, status_code=303)
    except Exception as e:
        return Div(f"Error creating checkout: {e}", cls="error-text")

@rt("/api/webhooks/stripe", methods=["POST"])
async def stripe_webhook(req):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        return "Invalid signature", 400

    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        org_id = session_data.get('metadata', {}).get('org_id')
        credits_str = session_data.get('metadata', {}).get('credits_to_add')
        session_id = session_data.get('id')
        
        if org_id and credits_str:
            try:
                # Add to ledger (will fail on duplicate webhook thanks to UNIQUE constraint)
                db_insert("billing_ledger", {
                    "org_id": org_id,
                    "stripe_session_id": session_id,
                    "amount_paid": session_data.get('amount_total', 0) / 100.0,
                    "credits_added": int(credits_str),
                    "status": "completed"
                })
                
                # Retrieve current balance and safely bump it
                orgs = db_select("organisations", {"id": org_id})
                if orgs:
                    current_balance = orgs[0].get("credit_balance", 0)
                    new_balance = current_balance + int(credits_str)
                    from app.supabase_db import supabase
                    supabase.table("organisations").update({"credit_balance": new_balance}).eq("id", org_id).execute()
            except Exception as e:
                print("Webhook processing error:", e)

    return "Success", 200

@rt("/api/v1/query", methods=["POST"])
async def api_v1_query(req):
    # 1. Extract Bearer Token
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        from starlette.responses import Response
        return Response('{"error": "Unauthorized"}', status_code=401, media_type="application/json")
    
    api_key = auth_header.split(" ")[1]
    
    try:
        # 2. Validate API Key
        ints = db_select("integrations", {"id": api_key, "type": "api"})
        if not ints:
            from starlette.responses import Response
            return Response('{"error": "Invalid or revoked API Key"}', status_code=403, media_type="application/json")
        
        project_id = ints[0]["project_id"]
        
        # 3. Get Project mapping
        projects = db_select("projects", {"id": project_id})
        if not projects:
            from starlette.responses import Response
            return Response('{"error": "Project not found"}', status_code=404, media_type="application/json")
        org_id = projects[0]["org_id"]
        
        # 4. Check Credit Balance
        orgs = db_select("organisations", {"id": org_id})
        if not orgs:
            from starlette.responses import Response
            return Response('{"error": "Organisation not found"}', status_code=404, media_type="application/json")
            
        credit_balance = orgs[0].get("credit_balance", 0)
        if credit_balance <= 0:
            from starlette.responses import Response
            return Response('{"error": "Payment Required. Credit balance is 0. Top up at app.opendata.london/billing"}', status_code=402, media_type="application/json")
            
        # 5. Extract JSON payload
        try:
            body = await req.json()
            sql_query = body.get("query")
            dataset_slug = body.get("dataset")
        except:
            from starlette.responses import Response
            return Response('{"error": "Invalid JSON payload. Expected {query: str, dataset: str}"}', status_code=400, media_type="application/json")
            
        # 6. Verify Dataset access
        if dataset_slug:
            has_access = db_select("dataset_integrations", {"integration_id": api_key, "dataset_slug": dataset_slug})
            if not has_access:
                from starlette.responses import Response
                return Response('{"error": "API Key does not have access to this dataset."}', status_code=403, media_type="application/json")
            
        # 7. Mock Snowflake Execution
        import asyncio
        await asyncio.sleep(0.3)
        mock_data = [{"example": "response", "source": dataset_slug or "global"}]
        
        # 8. Deduct 1 credit
        new_balance = credit_balance - 1
        from app.supabase_db import supabase
        supabase.table("organisations").update({"credit_balance": new_balance}).eq("id", org_id).execute()
        
        import json
        from starlette.responses import Response
        return Response(json.dumps({"status": "success", "credits_remaining": new_balance, "data": mock_data}), status_code=200, media_type="application/json")

    except Exception as e:
        print("API V1 ERROR:", e)
        from starlette.responses import Response
        return Response('{"error": "Internal Server Error"}', status_code=500, media_type="application/json")

# Settings and Billing moved to bottom or consolidated below

import time
from starlette.datastructures import UploadFile

@rt("/settings/avatar", methods=["POST"])
async def post_settings_avatar(session, avatar_file: UploadFile):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        
        file_bytes = await avatar_file.read()
        if not file_bytes:
            return RedirectResponse("/settings", status_code=303)
            
        filename = f"{org_id}/avatar_{int(time.time())}.png"
        
        from app.supabase_db import storage_upload
        public_url = storage_upload("org-avatars", filename, file_bytes, avatar_file.content_type)
        
        supabase.table("organisations").update({"avatar_url": public_url}).eq("id", org_id).execute()
        log_audit(org_id, user_id, "Updated organization avatar", "organisation", org_id)
        
        # FastHTML standard redirect logic handles standard form posts gracefully
        return RedirectResponse("/settings", status_code=303)
    except Exception as e:
        return Div(f"Failed to upload: {str(e)}", cls="error-text", style="margin-top: 8px;")

@rt("/settings/rename", methods=["POST"])
def post_settings_rename(session, org_name: str):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        
        # Perform DB Patch via Supabase client directly
        # Perform DB Patch via Supabase client directly (already defined globally as 'supabase')
        res = supabase.table('organisations').update({"name": org_name}).eq('id', org_id).execute()
        log_audit(org_id, user_id, f"Renamed organization to '{org_name}'", "organisation", org_id)
        session['force_header_refresh'] = True
        return Div("Organization name updated successfully.", cls="success-text", style="margin-top: 8px;")
    except Exception as e:
        return Div(f"Failed to update name: {e}", cls="error-text", style="margin-top: 8px;")

@rt("/settings/transfer", methods=["POST"])
def post_settings_transfer(session, target_user_id: str):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    
    try:
        from app.supabase_db import db_select
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        
        org_id = memberships[0]["org_id"]
        role = memberships[0].get("role", "member")
        
        if role != "owner":
            return Div("Only the organization owner can execute transfers.", cls="error-text", style="margin-top: 8px;")
            
        target = db_select("memberships", {"user_id": target_user_id, "org_id": org_id, "status": "active"})
        if not target:
            return Div("Target user is not an active team member.", cls="error-text", style="margin-top: 8px;")
            
        # Execute Role Swap 
        supabase.table("memberships").update({"role": "admin"}).eq("user_id", user_id).eq("org_id", org_id).execute()
        supabase.table("memberships").update({"role": "owner"}).eq("user_id", target_user_id).eq("org_id", org_id).execute()
        log_audit(org_id, user_id, f"Transferred ownership to user {target_user_id}", "organisation", org_id)
        
        return RedirectResponse("/settings", status_code=303)
    except Exception as e:
        return Div(f"Transfer failed: {str(e)}", cls="error-text", style="margin-top: 8px;")

@rt("/settings/delete", methods=["POST"])
def post_settings_delete(session):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        
        # Supabase client is already defined globally as 'supabase'
        res = supabase.table('organisations').delete().eq('id', org_id).execute()
        
        # Because cascading deleted the membership too, we bounce them to /projects landing
        return RedirectResponse("/projects", status_code=303)
    except Exception as e:
        return f"Failed to delete organization: {e}", 500

@rt("/settings/billing", methods=["POST"])
def post_settings_billing(session, billing_email: str):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    
    try:
        from app.supabase_db import db_select, supabase
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        
        supabase.table('organisations').update({"billing_email": billing_email}).eq('id', org_id).execute()
        log_audit(org_id, user_id, f"Updated billing email to '{billing_email}'", "organisation", org_id)
        
        return Div("Billing email updated successfully.", cls="success-text", style="margin-top: 8px;")
    except Exception as e:
        return Div(f"Failed to update billing email: {e}", cls="error-text", style="margin-top: 8px;")

@rt("/settings/sso", methods=["POST"])
def post_settings_sso(session, domain: str, metadata_url: str, is_active: bool = False):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    
    try:
        from app.supabase_db import db_select, supabase
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        
        # Upsert SSO Configuration
        supabase.table("sso_configurations").upsert({
            "org_id": org_id,
            "domain": domain,
            "metadata_url": metadata_url,
            "is_active": is_active
        }, on_conflict="org_id").execute()
        
        log_audit(org_id, user_id, f"Updated SSO configuration (Active: {is_active})", "sso", org_id)
        
        return Div("SSO configuration saved successfully.", cls="success-text", style="margin-top: 8px;")
    except Exception as e:
        return Div(f"Failed to save SSO config: {e}", cls="error-text", style="margin-top: 8px;")

@rt("/billing/spend-cap", methods=["POST"])
def post_billing_spend_cap(session, enabled: bool = False):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    try:
        from app.supabase_db import db_select, supabase
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        supabase.table("organisations").update({"spend_cap_enabled": enabled}).eq("id", org_id).execute()
        log_audit(org_id, user_id, f"{'Enabled' if enabled else 'Disabled'} billing spend cap", "billing", org_id)
        return "" # HTMX toggle doesn't need response body usually, but we could return a small toast
    except Exception: return "Error", 500

@rt("/billing/emails", methods=["POST"])
def post_billing_emails(session, billing_email: str, additional_emails: str = ""):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    try:
        from app.supabase_db import db_select, supabase
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        supabase.table("organisations").update({
            "billing_email": billing_email,
            "additional_billing_emails": additional_emails
        }).eq("id", org_id).execute()
        log_audit(org_id, user_id, "Updated billing email recipients", "billing", org_id)
        return Div("Billing emails saved.", cls="success-text", style="margin-top: 8px;")
    except Exception: return "Error", 500

@rt("/billing/address", methods=["POST"])
def post_billing_address(session, address: str, tax_id: str = ""):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    try:
        from app.supabase_db import db_select, supabase
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships: return "No active organization", 400
        org_id = memberships[0]["org_id"]
        supabase.table("organisations").update({
            "billing_address": address,
            "tax_id": tax_id
        }).eq("id", org_id).execute()
        log_audit(org_id, user_id, "Updated billing address and Tax ID", "billing", org_id)
        return Div("Billing address saved.", cls="success-text", style="margin-top: 8px;")
    except Exception: return "Error", 500

@rt("/org/switch", methods=["POST"])
def post_org_switch(session, org_id: str):
    user_id = _get_user_id(session)
    if not user_id: return "Unauthorized", 401
    try:
        from app.supabase_db import db_select
        # Verify user belongs to this org
        m = db_select("memberships", {"user_id": user_id, "org_id": org_id, "status": "active"})
        if not m: return "Unauthorized", 403
        
        session['active_org_id'] = org_id
        session.pop('active_project_id', None)
        session['force_header_refresh'] = True
        return Script("window.location.href = '/projects';")
    except Exception: return "Error", 500

@rt("/organisations")
def get_organisations(session):
    user_id = _get_user_id(session)
    user = session.get('user')
    if not user_id: return RedirectResponse("/login", status_code=303)
    
    m = db_select("memberships", {"user_id": user_id, "status": "active"})
    org_ids = [row["org_id"] for row in m]
    
    orgs = []
    if org_ids:
        try:
            # We use db_select but we need to fetch multiple by multiple IDs.
            # Since db_select only does 'eq' currently, I'll update it or do a manual fetch.
            # Actually, I'll just use a loop or better, update db_select to support 'in'.
            # For now, I'll use a manual httpx call as in supabase_db.py but here.
            from app.supabase_db import SUPABASE_URL, _headers
            import httpx
            ids_str = ",".join([str(i) for i in org_ids])
            url = f"{SUPABASE_URL}/rest/v1/organisations"
            r = httpx.get(url, params={"id": f"in.({ids_str})"}, headers=_headers())
            r.raise_for_status()
            orgs = r.json()
        except Exception as e:
            print(f"Error fetching orgs: {e}")
            orgs = []
        
    return page_layout("Organizations", "/organisations", user, OrganisationsPage(orgs), session=session)

@rt("/org/{slug}")
def get_org(slug: str, session):
    from app.pages.org_dashboard import OrgDashboard
    user = session.get('user')
    orgs = db_select("organisations", {"slug": slug})
    if not orgs: return "Organization not found", 404
    org = orgs[0]
    
    # Auto-set active org in session if they navigate here
    session['active_org_id'] = org['id']
    
    return page_layout(f"{org['name']} Dashboard", f"/org/{slug}", user, OrgDashboard(org), session=session)

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
        # Generate invite link via Supabase generate_link (free plan compatible)
        result = auth_invite(
            email=invited_email,
            redirect_to=f"{APP_URL}/invite/accept?org={slug}"
        )
        invite_link = result.get("action_link", "")
        # Send branded invite email via Resend
        email_sent = send_org_invite(
            invited_email=invited_email,
            org_name=org_name,
            role=role,
            invite_link=invite_link,
            invited_by=session.get('user', ''),
        )
        if email_sent:
            return Div(f"Invitation sent to {invited_email}.", cls="success-text")
        # Resend not configured — show the link for manual sharing
        return Div(
            P(f"Membership record created for {invited_email}.", style="color: #10B981; font-size: 13px; margin-bottom: 10px;"),
            P("Email delivery is not configured. Share this link manually:", style="color: #94A3B8; font-size: 13px; margin-bottom: 8px;"),
            Input(type="text", value=invite_link, readonly=True,
                  style="width: 100%; background: #0F1929; border: 1px solid rgba(148,163,184,0.2); color: #CBD5E1; padding: 8px 12px; border-radius: 6px; font-size: 12px; font-family: monospace;"),
        )
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
    return page_layout("Documentation", "/docs", session.get('user'), Div(H1("API Documentation", style="color: white;")), session=session)

@rt("/robots.txt")
def get_robots():
    from starlette.responses import PlainTextResponse
    content = """User-agent: *
Disallow: /dashboard
Disallow: /catalog
Disallow: /catalog/
Disallow: /keys
Disallow: /shares
Disallow: /queries
Disallow: /settings
Disallow: /admin
Disallow: /org/
Disallow: /create-org
Disallow: /invite/
Disallow: /auth/
Disallow: /debug/

# Login page is public but no value in indexing it
Disallow: /login
Disallow: /register
Disallow: /forgot-password
Disallow: /reset-password
"""
    return PlainTextResponse(content)

@rt("/projects/create", methods=["POST"])
def post_create_project(name: str, org_id: str, session):
    user_id = _get_user_id(session)
    if not user_id: return "unauthorized"
    try:
        new_p = db_insert("projects", {"org_id": org_id, "name": name.strip()})
        p_id = new_p[0]["id"]
        db_insert("project_members", {"project_id": p_id, "user_id": user_id, "role": "admin"})
        session['active_project_id'] = p_id
        log_audit(org_id, user_id, f"Created project '{name}'", "project", p_id)
        session['force_header_refresh'] = True
        return "ok"
    except Exception:
        return "error"

@rt("/projects/{p_id}/select", methods=["GET"])
def get_select_project(p_id: str, session):
    session['active_project_id'] = p_id
    return RedirectResponse("/projects", status_code=303)

@rt("/projects")
def get_projects(session):
    from app.pages.projects import ProjectsDashboard
    user_id = _get_user_id(session)
    if not user_id: return RedirectResponse("/login", status_code=303)
    return page_layout("Projects", "/projects", session.get('user'), ProjectsDashboard(user_id=user_id, session=session), session=session)

@rt("/team")
def get_team(session):
    return page_layout("Team", "/team", session.get('user'), Div(H1("Team Management (Coming Soon)", cls="fav-page-title"), P("Invite your organisation members here.", style="color:#64748B; margin-top: 10px;"), style="padding: 40px; text-align: center;"), session=session)

@rt("/usage")
def get_usage(session):
    return page_layout("Usage", "/usage", session.get('user'), Div(H1("Usage Data (Coming Soon)", cls="fav-page-title"), P("Monitor query execution stats and limits.", style="color:#64748B; margin-top: 10px;"), style="padding: 40px; text-align: center;"), session=session)

# Billing handled above

if __name__ == '__main__':
    # Ensure port is open, using 5002 since odl-web is likely 5001
    serve(port=5002)
