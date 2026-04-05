"""
Application factory — creates the FastHTML app and registers all routes.
"""
from fasthtml.common import Meta, fast_app, Beforeware

from app.config import SESSION_SECRET
from app.ui.styles import get_critical_canvas_style
from app.auth.middleware import before
from app.catalog.data import seed_catalog

# ── Create app ──
bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css'])
app, rt = fast_app(
    before=bware,
    secret_key=SESSION_SECRET,
    pico=False,
    surreal=False,
    hdrs=(
        get_critical_canvas_style(),
        Meta(name="theme-color", content="#09090b"),
    ),
)

# ── Seed catalog data on startup ──
try:
    seed_catalog()
except Exception as e:
    print(f"Startup warning: seed_catalog failed: {e}")

# ── Register feature routes ──
from app.auth.routes import register as _auth
from app.catalog.routes import register as _catalog
from app.integrations.routes import register as _integrations
from app.billing.routes import register as _billing
from app.billing.stripe_webhook import register as _stripe_wh
from app.orgs.routes import register as _orgs
from app.projects.routes import register as _projects
from app.team.routes import register as _team
from app.team.invite import register as _invite
from app.settings.routes import register as _settings
from app.api_v1.routes import register as _api_v1
from app.dashboard.routes import register as _dashboard
from app.explore.routes import register as _explore
from app.companies_graph.routes import register as _companies_graph

_auth(rt)
_catalog(rt)
_integrations(rt)
_billing(rt)
_stripe_wh(rt)
_orgs(rt)
_projects(rt)
_team(rt)
_invite(rt)
_settings(rt)
_api_v1(rt)
_dashboard(rt)
_explore(rt)
_companies_graph(rt)
