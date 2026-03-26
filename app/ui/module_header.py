"""
Top-level module header with brand, module slicer, and user controls.

The slicer provides navigation between core modules:
  Data Catalog  |  Explore
"""
from fasthtml.common import *
from app.ui.components import icon_svg, IC


# ── Module definitions ────────────────────────────────────────────────────────

MODULES = [
    ("Catalog",      "/catalog",    "catalog",  IC.book),
    ("Explore",      "/explore",    "explore",  IC.bolt),
]


# ── Header style ──────────────────────────────────────────────────────────────

MODULE_HEADER_STYLE = Style("""
    .module-header {
        background: linear-gradient(180deg, #1a1711 0%, #14120b 100%);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 1px 0 rgba(255,255,255,0.02);
        padding: 0 28px; height: 60px;
        display: flex; align-items: center; justify-content: space-between;
        position: sticky; top: 0; z-index: 1000;
    }

    .mh-left {
        display: flex; align-items: center; gap: 16px;
        flex: 1; min-width: 0;
    }

    .mh-brand {
        font-family: var(--font-display);
        font-weight: 600; font-size: 15px; color: var(--text-main);
        text-decoration: none; letter-spacing: -0.04em;
        white-space: nowrap;
    }
    .mh-brand:hover { color: var(--text-main); }

    /* ── Module slicer ──────────────────────────────────────────────────── */
    .mh-slicer-wrap {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        display: flex; justify-content: center;
    }

    .mh-slicer {
        display: flex; align-items: center;
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 12px; padding: 3px;
        gap: 2px;
        box-shadow: inset 0 1px 1px rgba(0,0,0,0.2);
    }

    .mh-slicer-btn {
        display: flex; align-items: center; gap: 8px;
        padding: 7px 16px; border-radius: 9px;
        font-family: var(--font-body);
        font-size: 13px; font-weight: 500;
        color: var(--text-muted); text-decoration: none;
        border: 1px solid transparent;
        background: transparent;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
        cursor: pointer;
    }

    .mh-slicer-btn:hover {
        color: var(--text-main);
        background: rgba(255,255,255,0.05);
    }

    .mh-slicer-btn.active {
        color: var(--text-main);
        background: rgba(2, 132, 199, 0.12);
        border-color: rgba(2, 132, 199, 0.3);
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2), 0 0 0 1px rgba(2, 132, 199, 0.05) inset;
    }
    .mh-slicer-btn.active .mh-slicer-icon {
        color: var(--accent);
    }

    .mh-slicer-icon {
        display: flex; align-items: center;
        color: var(--text-faint); transition: color 0.2s;
    }

    /* ── Right side ─────────────────────────────────────────────────────── */
    .mh-right {
        display: flex; align-items: center; gap: 16px;
        flex: 1; justify-content: flex-end;
    }

    .mh-context {
        display: flex; align-items: center; gap: 8px;
    }

    .mh-ctx-sep {
        color: var(--text-faint); font-weight: 300;
        font-size: 16px; user-select: none; opacity: 0.5;
    }

    .mh-user {
        color: var(--text-muted); font-size: 13px;
        font-family: var(--font-body);
    }

    .mh-settings-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 6px;
        border: 1px solid var(--border);
        color: var(--text-muted);
        text-decoration: none;
        transition: all 0.15s;
    }
    .mh-settings-link:hover {
        background: rgba(255,255,255,0.08);
        color: var(--text-main);
        border-color: var(--text-faint);
    }

    .mh-signout {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text-muted); padding: 5px 12px; border-radius: 5px;
        font-size: 13px; cursor: pointer;
        transition: all 0.15s; text-decoration: none;
        font-family: var(--font-body);
    }
    .mh-signout:hover {
        background: rgba(255,255,255,0.08); color: var(--text-main);
        border-color: var(--text-faint);
    }
""")


# ── Component ─────────────────────────────────────────────────────────────────

def odl_module_header(active_module="catalog", user=None):
    """Renders the top-level module header with the centered 3-way slicer."""

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

    # ── Sections ──
    left = Div(
        A("OpenData.London", href="/catalog", cls="mh-brand"),
        cls="mh-left"
    )

    center = Div(slicer, cls="mh-slicer-wrap")

    right_items = []
    if user:
        right_items.append(Div(user, cls="mh-user"))
        right_items.append(
            A(
                icon_svg(IC.cog, width="15", height="15"),
                href="/settings",
                cls="mh-settings-link",
                title="Settings",
                aria_label="Settings"
            )
        )
        right_items.append(A("Sign Out", href="/logout", cls="mh-signout"))

    right = Div(*right_items, cls="mh-right")

    return Header(
        MODULE_HEADER_STYLE,
        left, center, right,
        cls="module-header"
    )

