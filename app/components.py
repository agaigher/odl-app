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

def odl_sidebar(current_path="/"):
    
    def nav_item(label, path, icon="•"):
        exact_match_only = ("/", "/dashboard", "/favourites")
        is_active = current_path == path or (path not in exact_match_only and current_path.startswith(path))
        active_cls = "active" if is_active else ""
        return A(
            Span(icon, style="margin-right: 12px; font-size: 16px; opacity: 0.7;"),
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
                margin-bottom: 6px;
                padding: 0 8px;
            }
            .sidebar-item {
                display: flex;
                align-items: center;
                padding: 8px 12px;
                color: #475569;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 6px;
                margin-bottom: 2px;
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
        """),
        Div(
            Div("Home", cls="sidebar-title"),
            nav_item("Dashboard", "/dashboard", "⊞"),
            cls="sidebar-section"
        ),
        Div(
            Div("Discovery", cls="sidebar-title"),
            nav_item("Data Catalog", "/catalog", "⚲"),
            nav_item("Favourites", "/favourites", "☆"),
            nav_item("Saved Queries", "/queries", "★"),
            cls="sidebar-section"
        ),
        Div(
            Div("Workspace", cls="sidebar-title"),
            nav_item("Projects", "/projects", "📦"),
            nav_item("Team", "/team", "👥"),
            nav_item("Integrations", "/integrations", "⊞"),
            nav_item("Usage", "/usage", "📈"),
            nav_item("Billing", "/billing", "💲"),
            nav_item("Organization Settings", "/settings", "⚙"),
            cls="sidebar-section"
        ),
        cls="app-sidebar"
    )

def page_layout(page_title, current_path, user, *content):
    """Standard layout wrapper for all authenticated pages."""
    from app import get_app_style # inline to avoid circular issues
    
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
                odl_sidebar(current_path),
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
