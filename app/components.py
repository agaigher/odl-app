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
            cls="app-layout"
        )
    )
