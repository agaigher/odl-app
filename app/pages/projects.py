from fasthtml.common import *
from app.supabase_db import db_select, db_insert

def ProjectsDashboard(user_id="", session=None):
    from app.pages.catalog import CATALOG_STYLE
    
    # 1. Fetch the active Org
    active_org_id = session.get('active_org_id') if session else None
    
    if not active_org_id:
        # Fallback: try to find any org the user is in
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if memberships:
                active_org_id = memberships[0]["org_id"]
                if session: session['active_org_id'] = active_org_id
        except Exception:
            pass

    if not active_org_id:
        return Div(
            CATALOG_STYLE,
            Div(H1("Projects", cls="fav-page-title"), cls="fav-header"),
            Div("You must be part of an Organization to create Projects.", cls="error-text", style="padding:24px;")
        )
    
    # 2. Fetch Projects for active org
    try:
        projects = db_select("projects", {"org_id": active_org_id})
    except Exception:
        projects = []
        
    project_cards = []
    active_project_id = session.get('active_project_id')
    
    for p in projects:
        is_active = str(p["id"]) == str(active_project_id)
        active_badge = Span("Active", style="background:#0284C7; color:white; font-size:10px; padding:2px 6px; border-radius:4px; margin-left:12px; font-weight:700;") if is_active else ""
        
        project_cards.append(Div(
            Div(
                H3(p["name"], active_badge, style="font-size:16px; margin-bottom:8px; display:flex; align-items:center; color: #F8FAFC;"),
                P(f"Project ID: {p['id'][:8]}...", style="font-size:12px; color: #64748B;"),
                style="margin-bottom:16px;"
            ),
            Div(
                A("Open Project Dashboard →", href=f"/projects/{p['id']}/select", 
                  style="color:#0284C7; font-size:13px; font-weight:600; text-decoration: none;"),
                style="margin-top: auto;"
            ),
            cls="int-card",
            style="background: #1E293B; border: 1px solid rgba(255,255,255,0.06); padding: 24px; border-radius: 12px; height: 160px; display: flex; flex-direction: column;"
        ))

    new_proj_form = Form(
        Input(type="text", name="name", placeholder="New Project Name (e.g. Sales API)…", required=True, 
              style="background: #0F172A; border: 1px solid rgba(148,163,184,0.2); color: #F8FAFC; padding: 10px 14px; border-radius: 8px; font-size: 14px; flex: 1;"),
        Input(type="hidden", name="org_id", value=active_org_id),
        Button("+ Create Project", type="submit", 
               style="background: #0284C7; color: #0F172A; font-weight: 700; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer;"),
        hx_post="/projects/create",
        hx_on__after_request="if(event.detail.successful) window.location.reload()",
        style="display:flex; gap:12px; margin-top:16px; max-width: 600px;"
    )

    return Div(
        CATALOG_STYLE,
        Style("""
            .projects-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 24px;
                padding: 32px 40px;
            }
            .fav-header { padding: 32px 40px; border-bottom: 1px solid rgba(255,255,255,0.06); background: #0F172A; }
            .fav-page-title { font-size: 24px; font-weight: 700; color: #F8FAFC; margin-bottom: 8px; }
            .fav-page-sub { font-size: 14px; color: #64748B; }
        """),
        Div(
            H1("Projects", cls="fav-page-title"),
            P("Manage multiple environments and API access within this organization.", cls="fav-page-sub"),
            new_proj_form,
            cls="fav-header"
        ),
        Div(*project_cards, cls="projects-grid") if projects else 
        Div(
            Div(
                Img(src="https://img.icons8.com/isometric/100/null/folder-invoices.png", style="width: 80px; opacity: 0.5; margin-bottom: 20px; filter: grayscale(1);"),
                P("No projects found in this organization.", style="color: #64748B; font-size: 15px;"),
                P("Create your first project to start integrating data.", style="color: #475569; font-size: 13px; margin-top: 4px;"),
                style="text-align: center; padding: 100px 40px;"
            )
        )
    )
