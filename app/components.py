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
                background-color: #0b0c0c;
                border-bottom: 2px solid #29b5e8;
                padding: 0 30px;
                height: 65px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                position: sticky;
                top: 0;
                z-index: 1000;
            }
            .app-brand {
                font-weight: 700;
                font-size: 20px;
                color: #ffffff;
                text-decoration: none;
                font-family: "GDS Transport", arial, sans-serif;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .app-badge {
                background: rgba(41, 181, 232, 0.15);
                color: #29b5e8;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 700;
                font-family: 'Roboto Mono', monospace;
                letter-spacing: 0.5px;
            }
            .nav-actions {
                display: flex;
                align-items: center;
                gap: 20px;
            }
            .nav-user {
                color: #94A3B8;
                font-size: 14px;
            }
            .logout-btn {
                background: transparent;
                border: 1px solid #334155;
                color: #F8FAFC;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 13px;
                cursor: pointer;
                transition: background 0.2s;
                text-decoration: none;
            }
            .logout-btn:hover {
                background: #1E293B;
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
                width: 260px;
                background: #0B1120;
                border-right: 1px solid rgba(148, 163, 184, 0.1);
                padding: 24px 0;
                display: flex;
                flex-direction: column;
                flex-shrink: 0;
                overflow-y: auto;
            }
            .sidebar-section {
                padding: 0 24px;
                margin-bottom: 32px;
            }
            .sidebar-title {
                font-family: 'Roboto Mono', monospace;
                font-size: 11px;
                font-weight: 600;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            }
            .sidebar-item {
                display: flex;
                align-items: center;
                padding: 10px 16px;
                color: #CBD5E1;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 6px;
                margin-bottom: 4px;
                transition: all 0.2s;
            }
            .sidebar-item:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #F8FAFC;
            }
            .sidebar-item.active {
                background: rgba(41, 181, 232, 0.1);
                color: #29b5e8;
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
            Div("Access", cls="sidebar-title"),
            nav_item("API Keys", "/keys", "🔑"),
            nav_item("Snowflake Shares", "/shares", "❄"),
            cls="sidebar-section"
        ),
        Div(
            Div("Account", cls="sidebar-title"),
            nav_item("Settings", "/settings", "⚙"),
            nav_item("Documentation", "/docs", "📄"),
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
                    position: fixed; inset: 0; background: rgba(0,0,0,0.75);
                    display: flex; align-items: center; justify-content: center;
                    z-index: 9999;
                }
                .modal-box {
                    position: relative; background: #0F1929;
                    border: 1px solid rgba(148,163,184,0.18); border-radius: 12px;
                    padding: 28px; width: 380px; max-width: 92vw; z-index: 1;
                }
                .modal-title { font-size: 16px; font-weight: 700; color: #F8FAFC;
                    margin-bottom: 4px; }
                .modal-sub { font-size: 13px; color: #475569; margin-bottom: 20px;
                    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
                .modal-divider { border: none; border-top: 1px solid rgba(148,163,184,0.1);
                    margin: 16px 0; }
                .list-check-row { display: flex; align-items: center; gap: 10px;
                    padding: 8px 0; border-bottom: 1px solid rgba(148,163,184,0.06); }
                .list-check-row:last-child { border-bottom: none; }
                .list-check-row input[type=checkbox] { width: 16px; height: 16px;
                    accent-color: #29b5e8; cursor: pointer; flex-shrink: 0; }
                .list-check-name { font-size: 14px; color: #CBD5E1; flex: 1; }
                .modal-new-list { display: flex; gap: 8px; margin-top: 4px; }
                .modal-new-input {
                    flex: 1; background: #020617; border: 1px solid rgba(148,163,184,0.18);
                    color: #F8FAFC; padding: 8px 12px; border-radius: 6px;
                    font-family: 'Inter', sans-serif; font-size: 13px; outline: none;
                    transition: border-color 0.2s;
                }
                .modal-new-input:focus { border-color: #29b5e8; }
                .modal-new-input::placeholder { color: #334155; }
                .modal-create-btn {
                    background: rgba(41,181,232,0.1); color: #29b5e8; border: 1px solid rgba(41,181,232,0.25);
                    padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600;
                    cursor: pointer; font-family: 'Inter', sans-serif; white-space: nowrap;
                    transition: background 0.15s;
                }
                .modal-create-btn:hover { background: rgba(41,181,232,0.2); }
                .modal-done-btn {
                    background: #29b5e8; color: #020617; border: none;
                    padding: 9px 22px; border-radius: 6px; font-size: 13px; font-weight: 700;
                    cursor: pointer; font-family: 'Inter', sans-serif; float: right;
                    transition: opacity 0.15s;
                }
                .modal-done-btn:hover { opacity: 0.88; }
                .modal-empty { font-size: 13px; color: #475569; padding: 8px 0 12px; }
            """),
            cls="app-layout"
        )
    )
