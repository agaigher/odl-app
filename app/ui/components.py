"""
Shared UI primitives: navbar, sidebar, page_layout, icons.
"""
from fasthtml.common import *
import time

from dataclasses import dataclass


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
    cog = "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l-.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
    plus_circle = "M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"
    bolt = "M13 2L3 14h9l-1 8 10-12h-9l1-8z"
    chevron_up_down = "m7 15 5 5 5-5 M7 9l5-5 5 5"
    search = "M21 21l-4.35-4.35M19 11a8 8 0 11-16 0 8 8 0 0116 0z"
    check = "M20 6L9 17l-5-5"
    info = "M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z M12 16v-4 M12 8h.01"
    file_text = "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8"
    external_link = "M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6 M15 3h6v6 M10 14L21 3"
    chevron_left = "m15 18-6-6 6-6"
    chevron_right = "m9 18 6-6-6-6"
    credit_card = "M2 10h20 M2 6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6z"
    sun = "M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
    moon = "M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"


def icon_svg(d_path, width="18", height="18", **kwargs):
    if 'style' not in kwargs:
        kwargs['style'] = "display: block;"
    return Svg(
        NotStr(f'<path d="{d_path}"></path>'),
        xmlns="http://www.w3.org/2000/svg",
        width=width, height=height, viewBox="0 0 24 24",
        fill="none", stroke="currentColor",
        stroke_width="2", stroke_linecap="round", stroke_linejoin="round",
        **kwargs
    )


def OrgSwitcher(active_org, all_orgs):
    # Org switcher is intentionally disabled in the current header UX.
    return Div()


def ProjectSwitcher(active_project, all_projects):
    # Project switcher is intentionally disabled in the current header UX.
    return Div()


def odl_navbar(user=None, active_org=None, all_orgs=None, active_project=None, all_projects=None):
    user_display = Div(user, cls="nav-user") if user else Div()
    logout_btn = A("Sign Out", href="/logout", cls="logout-btn") if user else Div()
    actions = Div(user_display, logout_btn, cls="nav-actions")

    return Header(
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
            .app-navbar {
                background: #14120b;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                box-shadow: 0 1px 0 rgba(56, 189, 248, 0.1);
                padding: 0 28px; height: 56px;
                display: flex; align-items: center; justify-content: space-between;
                position: sticky; top: 0; z-index: 1000;
            }
            .nav-brand-wrap { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 10px; flex: 1; min-width: 0; }
            .app-logo { color: #F8FAFC; display: flex; align-items: center; text-decoration: none; }
            .brand-separator { color: rgba(148, 163, 184, 0.35); margin: 0 12px; font-weight: 300; font-size: 18px; }
            .org-switcher-container { position: relative; display: inline-block; }
            .org-switcher-trigger {
                background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
                color: #F8FAFC; padding: 6px 12px; border-radius: 6px;
                display: flex; align-items: center; gap: 8px; cursor: pointer; transition: all 0.2s;
            }
            .org-switcher-trigger:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); }
            .org-dropdown-panel {
                position: absolute; top: calc(100% + 8px); left: 0; width: 280px;
                background: #0f1219; border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px; box-shadow: 0 16px 48px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255,255,255,0.04);
                z-index: 1001; overflow: hidden;
            }
            .hidden { display: none !important; }
            .org-search-input { background: transparent; border: none; color: #F8FAFC; font-size: 13px; width: 100%; outline: none; }
            .org-item {
                display: flex; align-items: center; justify-content: space-between;
                padding: 10px 16px; color: #94A3B8; text-decoration: none; font-size: 13px;
                cursor: pointer; transition: 0.15s; background: transparent; border: none;
                width: 100%; text-align: left;
            }
            .org-item:hover { background: #334155; color: #F8FAFC; }
            .plan-pill {
                background: #1F2937; color: #94A3B8; font-size: 10px; font-weight: 700;
                padding: 2px 6px; border-radius: 4px; margin-left: 8px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .nav-actions { display: flex; align-items: center; gap: 16px; }
            .nav-user { color: #94A3B8; font-size: 13px; }
            .logout-btn {
                background: transparent; border: 1px solid rgba(255,255,255,0.1);
                color: #CBD5E1; padding: 5px 12px; border-radius: 5px;
                font-size: 13px; cursor: pointer; transition: all 0.15s; text-decoration: none;
            }
            .logout-btn:hover { background: rgba(255,255,255,0.08); color: #ffffff; }
        """),
        Div(
            A("OpenData.London", href="/projects", cls="app-logo",
              style="font-family: 'Space Grotesk', system-ui, sans-serif; font-weight: 600; font-size: 15px; color: #F8FAFC; text-decoration: none; letter-spacing: -0.04em;"),
            Span("FREE", cls="plan-pill") if active_org else None,
            cls="nav-brand-wrap"
        ),
        actions,
        cls="app-navbar"
    )


def odl_sidebar(current_path="/", org_name="Workspace", avatar_url=None, 
                active_org=None, all_orgs=None, active_project=None, all_projects=None,
                is_settings_module=False):
    def nav_item(label, path, icon_path):
        exact_match_only = ("/", "/dashboard", "/projects", "/favourites")
        is_active = current_path == path or (path not in exact_match_only and current_path.startswith(path))
        active_cls = "active" if is_active else ""
        return A(
            Span(icon_svg(icon_path), style="margin-right: 12px; display: flex; align-items: center; opacity: 0.85;"),
            label, href=path, cls=f"sidebar-item {active_cls}"
        )

    # ── Sidebar sections ──
    context_section = Div(
        Div(
            Img(src=avatar_url, style="width: 24px; height: 24px; border-radius: 4px; margin-right: 10px; object-fit: cover;") if avatar_url else
            Div(org_name[0].upper(), cls="sidebar-org-fallback"),
            Span(org_name, cls="sidebar-org-name"),
            style="display: flex; align-items: center; padding: 0 12px; margin-bottom: 20px;"
        ),
        Div("Home", cls="sidebar-title"),
        nav_item("Project Overview", "/dashboard", IC.grid),
        cls="sidebar-section"
    )

    return Nav(
        Style("""
            .app-sidebar {
                width: 240px; background: #14120b;
                border-right: 1px solid rgba(255,255,255,0.05);
                padding: 24px 0; display: flex; flex-direction: column; flex-shrink: 0;
                position: sticky; top: 60px; height: calc(100vh - 60px); overflow-y: auto;
            }
            .sidebar-section { padding: 0 16px; margin-bottom: 24px; }
            .sidebar-org-fallback {
                width: 24px; height: 24px; border-radius: 4px; margin-right: 10px;
                background: #374151; color: #fff; font-size: 11px; font-weight: 700;
                display: flex; align-items: center; justify-content: center; flex-shrink: 0;
            }
            .sidebar-org-name {
                font-weight: 600; font-size: 14px; color: var(--text-main);
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            }
            html[data-theme="light"] .sidebar-org-fallback {
                background: #e2e8f0; color: #475569;
            }
            .sidebar-title {
                font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 700;
                color: #4B5563; text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 8px; padding: 0 12px;
            }
            .sidebar-item {
                display: flex; align-items: center; padding: 8px 12px; color: #9CA3AF;
                text-decoration: none; font-size: 13px; font-weight: 500;
                border-radius: 6px; margin-bottom: 2px; transition: all 0.15s;
            }
            .sidebar-item:hover { background: rgba(255,255,255,0.05); color: #F9FAFB; }
            .sidebar-item.active {
                background: rgba(255,255,255,0.06); color: #FFFFFF; font-weight: 600;
                box-shadow: inset 2px 0 0 0 rgba(2, 132, 199, 0.65);
            }
            .sidebar-item.active span { opacity: 1; color: #0284C7; }
            html[data-theme="light"] .app-sidebar {
                background: #ffffff;
                border-right: 1px solid var(--border);
            }
            html[data-theme="light"] .sidebar-title { color: #94a3b8; }
            html[data-theme="light"] .sidebar-item { color: #475569; }
            html[data-theme="light"] .sidebar-item:hover {
                background: rgba(15,23,42,0.05); color: #0f172a;
            }
            html[data-theme="light"] .sidebar-item.active {
                background: rgba(2,132,199,0.08); color: #0f172a;
                box-shadow: inset 2px 0 0 0 rgba(2, 132, 199, 0.65);
            }
        """),
        context_section,
        Div(
            Div("Discovery", cls="sidebar-title"),
            nav_item("Data Catalog", "/catalog", IC.book),
            nav_item("Favourites", "/favourites", IC.star),
            nav_item("SQL Queries", "/queries", IC.code),
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


def _resolve_org_project_context(user, session):
    """Shared helper to resolve org/project context from session cache or DB."""
    org_name = "Organization"
    avatar_url = None
    active_org = None
    all_orgs = []
    active_project = None
    all_projects = []

    if user:
        try:
            from app.db import db_select, get_user_id_from_session
            u_id = user.get('id') if isinstance(user, dict) else None
            if not u_id and session:
                u_id = get_user_id_from_session(session)

            if u_id:
                now = time.time()
                cache = session.get('header_cache', {})
                use_cache = cache.get('expiry', 0) > now and session.get('force_header_refresh') is not True

                if use_cache:
                    all_orgs = cache.get('all_orgs', [])
                    active_id = session.get('active_org_id')
                    active_org = (
                        next((o for o in all_orgs if str(o["id"]) == str(active_id)), None)
                        if active_id else None
                    )
                    if not active_org and all_orgs:
                        active_org = all_orgs[0]
                        session['active_org_id'] = active_org['id']

                    if active_org:
                        org_name = active_org["name"]
                        avatar_url = active_org.get("avatar_url")
                        all_projects = cache.get('projects_map', {}).get(str(active_org['id']), [])
                        active_p_id = session.get('active_project_id')
                        active_project = (
                            next((p for p in all_projects if str(p["id"]) == str(active_p_id)), None)
                            if active_p_id else None
                        )
                        if not active_project and all_projects:
                            active_project = all_projects[0]
                            session['active_project_id'] = active_project['id']
                else:
                    memberships = db_select("memberships", {"user_id": u_id, "status": "active"})
                    if memberships:
                        org_ids = [m["org_id"] for m in memberships]
                        all_orgs = db_select("organisations", {"id": org_ids})

                        active_id = session.get('active_org_id')
                        if active_id:
                            active_org = next((o for o in all_orgs if str(o["id"]) == str(active_id)), None)

                        if not active_org and all_orgs:
                            active_org = all_orgs[0]
                            session['active_org_id'] = active_org['id']

                        if active_org:
                            org_name = active_org["name"]
                            avatar_url = active_org.get("avatar_url")
                            all_projects = db_select("projects", {"org_id": active_org["id"]})

                            active_p_id = session.get('active_project_id')
                            if active_p_id:
                                active_project = next((p for p in all_projects if str(p["id"]) == str(active_p_id)), None)

                            if not active_project and all_projects:
                                active_project = all_projects[0]
                                session['active_project_id'] = active_project['id']

                        projects_map = cache.get('projects_map', {})
                        if active_org:
                            projects_map[str(active_org['id'])] = all_projects

                        session['header_cache'] = {
                            'all_orgs': all_orgs,
                            'projects_map': projects_map,
                            'expiry': now + 300,
                        }
                        session.pop('force_header_refresh', None)
        except Exception as e:
            print(f"Error in layout context resolution: {e}")

    return org_name, avatar_url, active_org, all_orgs, active_project, all_projects


MODAL_STYLE = Style("""
    .modal-backdrop {
        position: fixed; inset: 0; background: rgba(2,6,15,0.72);
        display: flex; align-items: center; justify-content: center; z-index: 9999;
    }
    html[data-theme="light"] .modal-backdrop {
        background: rgba(15,23,42,0.35);
    }
    .modal-box {
        position: relative; background: rgba(15,23,42,0.98);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
        padding: 28px; width: 400px; max-width: 92vw; z-index: 1;
        box-shadow: 0 24px 64px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.04) inset;
    }
    html[data-theme="light"] .modal-box {
        background: #ffffff;
        border: 1px solid var(--border);
        box-shadow: var(--shadow), 0 0 0 1px rgba(15,23,42,0.04) inset;
    }
    .modal-title { font-size: 16px; font-weight: 600; color: #F1F5F9; margin-bottom: 4px; }
    html[data-theme="light"] .modal-title { color: var(--text-main); }
    .modal-sub { font-size: 13px; color: #94A3B8; margin-bottom: 20px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    html[data-theme="light"] .modal-sub { color: var(--text-muted); }
    .modal-divider { border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 16px 0; }
    .list-check-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
    .list-check-row:last-child { border-bottom: none; }
    .list-check-row input[type=checkbox] { width: 16px; height: 16px; accent-color: #0284C7; cursor: pointer; flex-shrink: 0; }
    .list-check-name { font-size: 14px; color: #E2E8F0; flex: 1; }
    html[data-theme="light"] .list-check-name { color: var(--text-main); }
    .modal-new-list { display: flex; gap: 8px; margin-top: 4px; }
    .modal-new-input {
        flex: 1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
        color: #F1F5F9; padding: 8px 12px; border-radius: 6px;
        font-family: 'Inter', sans-serif; font-size: 13px; outline: none; transition: border-color 0.2s;
    }
    html[data-theme="light"] .modal-new-input {
        background: var(--bg-muted);
        border: 1px solid var(--border);
        color: var(--text-main);
    }
    .modal-new-input:focus { border-color: rgba(56,189,248,0.35); box-shadow: 0 0 0 1px rgba(2,132,199,0.12); }
    .modal-new-input::placeholder { color: #64748B; }
    .modal-create-btn {
        background: rgba(2,132,199,0.15); color: #7dd3fc; border: 1px solid rgba(56,189,248,0.25);
        padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600;
        cursor: pointer; font-family: 'Inter', sans-serif; white-space: nowrap; transition: background 0.15s;
    }
    .modal-create-btn:hover { background: rgba(2,132,199,0.22); }
    .modal-done-btn {
        background: #0284C7; color: #ffffff; border: none;
        padding: 9px 22px; border-radius: 6px; font-size: 13px; font-weight: 600;
        cursor: pointer; font-family: 'Inter', sans-serif; float: right; transition: background 0.15s;
    }
    .modal-done-btn:hover { background: #0369A1; }
    .modal-empty { font-size: 13px; color: #94A3B8; padding: 8px 0 12px; }
    html[data-theme="light"] .modal-empty { color: var(--text-muted); }
""")


def module_page_layout(page_title, current_path, user, *content,
                       session=None, active_module="settings",
                       show_sidebar=True, full_width=False):
    """New layout wrapper using the module header with the 3-way slicer."""
    from app.ui.styles import get_app_style
    from app.ui.module_header import odl_module_header

    org_name, avatar_url, active_org, all_orgs, active_project, all_projects = \
        _resolve_org_project_context(user, session)

    # Build body children
    header = odl_module_header(
        active_module=active_module,
        user=user,
    )

    if show_sidebar:
        body_content = Div(
            header,
            Div(
                odl_sidebar(
                    current_path, org_name, avatar_url,
                    active_org=active_org, all_orgs=all_orgs,
                    active_project=active_project, all_projects=all_projects,
                    is_settings_module=(active_module == "settings")
                ),
                Main(*content, cls=f"main-content {'full-width' if full_width else ''}"),
                cls="app-container"
            ),
            Div(id="modal-root"),
            MODAL_STYLE,
            cls="app-layout"
        )
    else:
        body_content = Div(
            header,
            Main(*content, cls=f"main-content {'full-width' if full_width else ''}"),
            Div(id="modal-root"),
            MODAL_STYLE,
            cls="app-layout"
        )

    theme_init = Script("""
(function(){
  try {
    var k='odl-theme', s=localStorage.getItem(k);
    if(!s) s = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', s);
  } catch(e) {}
})();
""")
    theme_toggle = Script("""
document.addEventListener('DOMContentLoaded', function() {
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;
  btn.addEventListener('click', function() {
    var cur = document.documentElement.getAttribute('data-theme') || 'dark';
    var next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('odl-theme', next); } catch(e) {}
  });
});
""")

    return Html(
        Head(
            Title(f"{page_title} | ODL App"),
            theme_init,
            Script(src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.6/dist/htmx.min.js"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500;600;700&display=swap"),
            get_app_style(),
            theme_toggle,
        ),
        Body(body_content, cls="app-layout")
    )


def page_layout(page_title, current_path, user, *content, session=None, full_width=False):
    """Standard layout wrapper — delegates to module_page_layout with Settings module active."""
    return module_page_layout(
        page_title, current_path, user, *content,
        session=session, active_module="settings",
        show_sidebar=True, full_width=full_width,
    )
