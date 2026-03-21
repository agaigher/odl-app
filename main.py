import os
from dotenv import load_dotenv
from supabase_auth import SyncGoTrueClient
from fasthtml.common import *
from app.components import page_layout
from app.pages.catalog import DataCatalog
from app.pages.dataset import DatasetDetail
from app.pages.access import SettingsKeys, SettingsShares
from app.pages.auth import AuthPage

load_dotenv()

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

def before(req, session):
    open_routes = ['/login', '/register', '/forgot-password', '/reset-password',
                   '/auth/google', '/auth/github', '/auth/callback']
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

@rt("/")
def get(session):
    return page_layout("Data Catalog", "/", session.get('user'), DataCatalog())

@rt("/catalog/search")
def get_catalog_search(q: str):
    from app.pages.catalog import SearchCatalogResults
    return SearchCatalogResults(q)

@rt("/catalog/{slug}")
def get_dataset(slug: str, session):
    return page_layout("Dataset Details", f"/catalog/{slug}", session.get('user'), DatasetDetail(slug))

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

@rt("/docs")
def get_docs(session):
    return page_layout("Documentation", "/docs", session.get('user'), Div(H1("API Documentation", style="color: white;")))

if __name__ == '__main__':
    # Ensure port is open, using 5002 since odl-web is likely 5001
    serve(port=5002)
