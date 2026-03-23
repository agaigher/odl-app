from fasthtml.common import *
from app.db import *

def odl_navbar(user=None):
    # Simplifed version of odl-web navbar for the App interface
    user_display = Div(user, cls="nav-user") if user else Div()
    logout_btn = A("Sign Out", href="/logout", cls="logout-btn") if user else Div()
    actions = Div(user_display, logout_btn, cls="nav-actions")
    
    return Header(
        Style("""
            .app-navbar {
                background-color: #1E293B;
                border-bottom: 2px solid #0284C7;
                padding: 0 28px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                position: sticky;
                top: 0;
                z-index: 1000;
            }
            .app-brand {
                font-weight: 700;
                font-size: 18px;
                color: #ffffff;
                text-decoration: none;
                font-family: "GDS Transport", arial, sans-serif;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .app-badge {
                background: rgba(2,132,199,0.2);
                color: #7DD3FC;
                padding: 3px 7px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 700;
                font-family: 'Roboto Mono', monospace;
                letter-spacing: 0.5px;
            }
            .nav-actions {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            .nav-user {
                color: #94A3B8;
                font-size: 13px;
            }
            .logout-btn {
                background: transparent;
                border: 1px solid rgba(148,163,184,0.3);
                color: #CBD5E1;
                padding: 5px 12px;
                border-radius: 5px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.15s;
                text-decoration: none;
            }
            .logout-btn:hover {
                background: rgba(255,255,255,0.08);
                color: #ffffff;
            }
        """),
        A(
            "OpenData.London", 
            Div("APP", cls="app-badge"),
            href="/", 
            cls="app-brand"
        ),
        actions,
        cls="app-navbar"
    )

def odl_sidebar(current_path="/", org_name="Workspace", avatar_url=None):
    
    @dataclass
    class IC:
        grid = "M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z"
        book = "M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"
        star = "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
        code = "m18 16 4-4-4-4 M6 8 2 12l4 4 M14.5 4l-5 16"
        box = "M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z M3.27 6.96L12 12.01l8.73-5.05 M12 22.08V12"
        users = "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M23 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75"
        link = "M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71 M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"
        chart = "M18 20V10 M12 20V4 M6 20v-6"
        wallet = "M21 12V7H5a2 2 0 0 1 0-4h14v2 M3 5v14a2 2 0 0 0 2 2h16v-5H5"
        cog = "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"

    def icon_svg(d_path):
        return Svg(
            NotStr(f'<path d="{d_path}"></path>'),
            xmlns="http://www.w3.org/2000/svg",
            width="18", height="18", viewBox="0 0 24 24",
            fill="none", stroke="currentColor",
            stroke_width="2", stroke_linecap="round", stroke_linejoin="round",
            style="display: block;"
        )

    def nav_item(label, path, icon_path):
        exact_match_only = ("/", "/dashboard", "/favourites")
        is_active = current_path == path or (path not in exact_match_only and current_path.startswith(path))
        active_cls = "active" if is_active else ""
        return A(
            Span(icon_svg(icon_path), style="margin-right: 12px; display: flex; align-items: center; opacity: 0.85;"),
            label,
            href=path,
            cls=f"sidebar-item {active_cls}"
        )

    return Nav(
        Style("""
            .app-sidebar {
                width: 240px;
                background: #FFFFFF;
                border-right: 1px solid #E2E8F0;
                padding: 20px 0;
                display: flex;
                flex-direction: column;
                flex-shrink: 0;
                overflow-y: auto;
            }
            .sidebar-section {
                padding: 0 16px;
                margin-bottom: 28px;
            }
            .sidebar-title {
                font-family: 'Inter', sans-serif;
                font-size: 10px;
                font-weight: 700;
                color: #94A3B8;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                margin-bottom: 8px;
                padding: 0 8px;
            }
            .sidebar-item {
                display: flex;
                align-items: center;
                padding: 9px 12px;
                color: #475569;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 6px;
                margin-bottom: 4px;
                transition: all 0.15s;
            }
            .sidebar-item:hover {
                background: #F1F5F9;
                color: #1E293B;
            }
            .sidebar-item.active {
                background: #E0F2FE;
                color: #0284C7;
                font-weight: 600;
            }
            .sidebar-item.active span {
                opacity: 1;
            }
        """),
        Div(
            Div(
                Img(src=avatar_url, style="width: 24px; height: 24px; border-radius: 4px; margin-right: 12px; object-fit: cover;") if avatar_url else None,
                Span(org_name, style="font-weight: 700; font-size: 15px; color: #0F172A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"),
                style="display: flex; align-items: center; padding: 0 16px; margin-bottom: 28px;"
            ),
            Div("Home", cls="sidebar-title"),
            nav_item("Dashboard", "/dashboard", IC.grid),
            cls="sidebar-section"
        ),
        Div(
            Div("Discovery", cls="sidebar-title"),
            nav_item("Data Catalog", "/catalog", IC.book),
            nav_item("Favourites", "/favourites", IC.star),
            nav_item("Saved Queries", "/queries", IC.code),
            cls="sidebar-section"
        ),
        Div(
            Div("Workspace", cls="sidebar-title"),
            nav_item("Projects", "/projects", IC.box),
            nav_item("Team", "/team", IC.users),
            nav_item("Integrations", "/integrations", IC.link),
            nav_item("Usage", "/usage", IC.chart),
            nav_item("Billing", "/billing", IC.wallet),
            nav_item("Organization Settings", "/settings", IC.cog),
            cls="sidebar-section"
        ),
        cls="app-sidebar"
    )

def page_layout(page_title, current_path, user, *content):
    """Standard layout wrapper for all authenticated pages."""
    from app import get_app_style # inline to avoid circular issues
    
    org_name = "Workspace"
    avatar_url = None
    if user:
        try:
            from app.supabase_db import db_select
            m = db_select("memberships", {"user_id": user["id"], "status": "active"})
            if m:
                orgs = db_select("organisations", {"id": m[0]["org_id"]})
                if orgs:
                    org_name = orgs[0]["name"]
                    avatar_url = orgs[0].get("avatar_url")
        except: pass
    
    return Html(
        Head(
            Title(f"{page_title} | ODL App"),
            Script(src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.6/dist/htmx.min.js"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500;600;700&display=swap"),
            get_app_style()
        ),
        Body(
            odl_navbar(user),
            Div(
                odl_sidebar(current_path, org_name, avatar_url),
                Main(
                    *content,
                    cls="main-content"
                ),
                cls="app-container"
            ),
            # Modal root — favourite list picker renders here
            Div(id="modal-root"),
            Style("""
                .modal-backdrop {
                    position: fixed; inset: 0; background: rgba(15,23,42,0.5);
                    display: flex; align-items: center; justify-content: center;
                    z-index: 9999;
                }
                .modal-box {
                    position: relative; background: #FFFFFF;
                    border: 1px solid #E2E8F0; border-radius: 12px;
                    padding: 28px; width: 400px; max-width: 92vw; z-index: 1;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
                }
                .modal-title { font-size: 16px; font-weight: 700; color: #1E293B;
                    margin-bottom: 4px; }
                .modal-sub { font-size: 13px; color: #94A3B8; margin-bottom: 20px;
                    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
                .modal-divider { border: none; border-top: 1px solid #F1F5F9;
                    margin: 16px 0; }
                .list-check-row { display: flex; align-items: center; gap: 10px;
                    padding: 8px 0; border-bottom: 1px solid #F8FAFC; }
                .list-check-row:last-child { border-bottom: none; }
                .list-check-row input[type=checkbox] { width: 16px; height: 16px;
                    accent-color: #0284C7; cursor: pointer; flex-shrink: 0; }
                .list-check-name { font-size: 14px; color: #374151; flex: 1; }
                .modal-new-list { display: flex; gap: 8px; margin-top: 4px; }
                .modal-new-input {
                    flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0;
                    color: #1E293B; padding: 8px 12px; border-radius: 6px;
                    font-family: 'Inter', sans-serif; font-size: 13px; outline: none;
                    transition: border-color 0.2s;
                }
                .modal-new-input:focus { border-color: #0284C7; box-shadow: 0 0 0 3px rgba(2,132,199,0.1); }
                .modal-new-input::placeholder { color: #CBD5E1; }
                .modal-create-btn {
                    background: #E0F2FE; color: #0284C7; border: 1px solid #BAE6FD;
                    padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600;
                    cursor: pointer; font-family: 'Inter', sans-serif; white-space: nowrap;
                    transition: background 0.15s;
                }
                .modal-create-btn:hover { background: #BAE6FD; }
                .modal-done-btn {
                    background: #0284C7; color: #ffffff; border: none;
                    padding: 9px 22px; border-radius: 6px; font-size: 13px; font-weight: 700;
                    cursor: pointer; font-family: 'Inter', sans-serif; float: right;
                    transition: background 0.15s;
                }
                .modal-done-btn:hover { background: #0369A1; }
                .modal-empty { font-size: 13px; color: #94A3B8; padding: 8px 0 12px; }
            """),
            cls="app-layout"
        )
    )
