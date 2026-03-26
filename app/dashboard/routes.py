"""
Dashboard and misc routes: home, project overview, usage, docs, queries, robots.txt.
"""
from fasthtml.common import *
from starlette.responses import PlainTextResponse

from app.auth.middleware import get_user_id
from app.ui.components import page_layout
from app.pages.dashboard import Dashboard

ENTRY_ROUTE = "/catalog"


def register(rt):

    @rt("/")
    def get_home(session):
        return RedirectResponse(ENTRY_ROUTE, status_code=303)

    @rt("/dashboard")
    def get_dashboard(session):
        user_email = session.get('user', '')
        user_id = get_user_id(session)
        return page_layout("Project Overview", "/dashboard", user_email,
                           Dashboard(user_id=str(user_id or ""), user_email=user_email), session=session)

    @rt("/usage")
    def get_usage(session):
        from app.pages.usage import UsageDashboard
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        return page_layout("Usage", "/usage", session.get('user'),
                           UsageDashboard(user_id=user_id, session=session))

    @rt("/queries")
    def get_queries(session):
        return page_layout("SQL Queries", "/queries", session.get('user'),
                           Div(H1("Coming Soon", style="color: white;")), session=session)

    @rt("/docs")
    def get_docs(session):
        return page_layout("Documentation", "/docs", session.get('user'),
                           Div(H1("API Documentation", style="color: white;")), session=session)

    @rt("/robots.txt")
    def get_robots():
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
