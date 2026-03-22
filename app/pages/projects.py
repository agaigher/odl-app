from fasthtml.common import *
from app.supabase_db import db_select, db_insert

def ProjectsDashboard(user_id="", session=None):
    from app.pages.catalog import CATALOG_STYLE
    
    # 1. Fetch which Orgs the user is in
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        org_ids = [m["org_id"] for m in memberships]
    except Exception:
        org_ids = []

    if not org_ids:
        return Div(
            CATALOG_STYLE,
            Div(H1("Projects", cls="fav-page-title"), cls="fav-header"),
            Div("You must be part of an Organisation to create Projects.", cls="error-text", style="padding:24px;")
        )
    
    org_id = org_ids[0]

    # 2. Fetch Projects
    try:
        projects = db_select("projects", {"org_id": org_id})
    except Exception:
        projects = []
        
    project_cards = []
    active_project_id = session.get('active_project_id')
    
    for p in projects:
        is_active = p["id"] == active_project_id
        active_badge = Span("Active", style="background:#10B981;color:white;font-size:11px;padding:2px 6px;border-radius:4px;margin-left:8px;") if is_active else ""
        
        project_cards.append(Div(
            Div(
                H3(p["name"], active_badge, style="font-size:16px; margin-bottom:8px; display:flex; align-items:center;"),
                style="margin-bottom:12px;"
            ),
            A("Switch to Project →", href=f"/projects/{p['id']}/select", cls="fav-ds-title", style="color:#0284C7; font-size:14px;"),
            cls="int-card"
        ))

    new_proj_form = Form(
        Input(type="text", name="name", placeholder="New Project Name (e.g. Prod API)…", required=True, cls="fav-new-input", style="flex:1;"),
        Input(type="hidden", name="org_id", value=org_id),
        Button("+ Create Project", type="submit", cls="fav-create-btn"),
        hx_post="/projects/create",
        hx_on__after_request="if(event.detail.successful) window.location.reload()",
        style="display:flex; gap:8px; margin-top:8px;"
    )

    return Div(
        CATALOG_STYLE,
        Div(
            H1("Projects", cls="fav-page-title"),
            new_proj_form,
            cls="fav-header",
            style="flex-direction: column; align-items: stretch; gap: 8px;"
        ),
        Div(*project_cards, id="project-list", cls="int-grid") if projects else Div(P("No projects yet. Create your first one above!"), cls="empty-msg", style="padding:24px;")
    )
