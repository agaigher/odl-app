"""
Top-level module header with brand, module slicer, and user controls.

The slicer provides navigation between the three main modules:
  Data Catalog  |  Explore  |  Settings
"""
from fasthtml.common import *
from app.ui.components import icon_svg, IC, OrgSwitcher, ProjectSwitcher


# ── Module definitions ────────────────────────────────────────────────────────

MODULES = [
    ("Data Catalog", "/catalog",    "catalog",  IC.book),
    ("Explore",      "/explore",    "explore",  IC.bolt),
    ("Settings",     "/projects",   "settings", IC.cog),
]


# ── Header style ──────────────────────────────────────────────────────────────

MODULE_HEADER_STYLE = Style("""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

    .module-header {
        background: linear-gradient(180deg, #0c0e14 0%, #080a0f 100%);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 1px 0 rgba(56, 189, 248, 0.08);
        padding: 0 28px; height: 56px;
        display: flex; align-items: center; justify-content: space-between;
        position: sticky; top: 0; z-index: 1000;
    }

    .mh-left {
        display: flex; align-items: center; gap: 24px;
    }

    .mh-brand {
        font-family: 'Space Grotesk', system-ui, sans-serif;
        font-weight: 600; font-size: 15px; color: #F8FAFC;
        text-decoration: none; letter-spacing: -0.04em;
        white-space: nowrap;
    }
    .mh-brand:hover { color: #F8FAFC; }

    .mh-separator {
        width: 1px; height: 24px;
        background: rgba(148, 163, 184, 0.2);
    }

    /* ── Module slicer ──────────────────────────────────────────────────── */
    .mh-slicer {
        display: flex; align-items: center;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px; padding: 3px;
        gap: 2px;
    }

    .mh-slicer-btn {
        display: flex; align-items: center; gap: 7px;
        padding: 7px 16px; border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 13px; font-weight: 500;
        color: #94A3B8; text-decoration: none;
        border: 1px solid transparent;
        background: transparent;
        transition: all 0.18s ease;
        white-space: nowrap;
        cursor: pointer;
    }

    .mh-slicer-btn:hover {
        color: #E2E8F0;
        background: rgba(255,255,255,0.06);
    }

    .mh-slicer-btn.active {
        color: #F8FAFC;
        background: rgba(255,255,255,0.08);
        border-color: rgba(255,255,255,0.1);
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }
    .mh-slicer-btn.active .mh-slicer-icon {
        color: #38bdf8;
    }

    .mh-slicer-icon {
        display: flex; align-items: center;
        color: #64748B; transition: color 0.18s;
    }

    /* ── Right side ─────────────────────────────────────────────────────── */
    .mh-right {
        display: flex; align-items: center; gap: 12px;
    }

    .mh-context {
        display: flex; align-items: center; gap: 8px;
    }

    .mh-ctx-sep {
        color: rgba(148, 163, 184, 0.35); font-weight: 300;
        font-size: 16px; user-select: none;
    }

    .mh-user {
        color: #94A3B8; font-size: 13px;
        font-family: 'Inter', sans-serif;
    }

    .mh-signout {
        background: transparent;
        border: 1px solid rgba(255,255,255,0.1);
        color: #CBD5E1; padding: 5px 12px; border-radius: 5px;
        font-size: 13px; cursor: pointer;
        transition: all 0.15s; text-decoration: none;
        font-family: 'Inter', sans-serif;
    }
    .mh-signout:hover {
        background: rgba(255,255,255,0.08); color: #ffffff;
    }
""")


# ── Component ─────────────────────────────────────────────────────────────────

def odl_module_header(active_module="catalog", user=None,
                      active_org=None, all_orgs=None,
                      active_project=None, all_projects=None):
    """Renders the top-level module header with the 3-way slicer."""

    # ── Module slicer buttons ──
    slicer_btns = []
    for label, href, key, icon_path in MODULES:
        is_active = key == active_module
        slicer_btns.append(
            A(
                Span(icon_svg(icon_path, width="14", height="14"), cls="mh-slicer-icon"),
                label,
                href=href,
                cls=f"mh-slicer-btn {'active' if is_active else ''}"
            )
        )

    slicer = Div(*slicer_btns, cls="mh-slicer")

    # ── Left section ──
    left = Div(
        A("OpenData.London", href="/catalog", cls="mh-brand"),
        Div(cls="mh-separator"),
        slicer,
        cls="mh-left"
    )

    # ── Right section ──
    right_items = []

    # Compact org / project context
    if active_org or all_orgs:
        right_items.append(
            Div(
                OrgSwitcher(active_org, all_orgs),
                Span("/", cls="mh-ctx-sep"),
                ProjectSwitcher(active_project, all_projects),
                cls="mh-context"
            )
        )

    if user:
        right_items.append(Div(user, cls="mh-user"))
        right_items.append(A("Sign Out", href="/logout", cls="mh-signout"))

    right = Div(*right_items, cls="mh-right")

    return Header(
        MODULE_HEADER_STYLE,
        left, right,
        cls="module-header"
    )
