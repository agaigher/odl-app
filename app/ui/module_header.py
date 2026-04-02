"""
Top-level module header with brand, module slicer, and user controls.
"""
from fasthtml.common import *

from app.ui.components import IC, icon_svg


MODULES = [
    ("Catalog", "/catalog", "catalog", IC.book),
    ("Explore", "/explore", "explore", IC.bolt),
]


MODULE_HEADER_STYLE = Style("""
    .module-header {
        background: linear-gradient(180deg, var(--bg-elevated) 0%, var(--bg-page) 100%);
        border-bottom: 1px solid var(--border);
        box-shadow: 0 1px 0 var(--border-subtle);
        padding: 0 28px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    .mh-left {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1;
        min-width: 0;
    }
    .mh-brand {
        font-family: var(--font-display);
        font-weight: 600;
        font-size: 15px;
        color: var(--text-main);
        text-decoration: none;
        letter-spacing: -0.04em;
        white-space: nowrap;
    }
    .mh-brand:hover { color: var(--text-main); }
    .mh-slicer-wrap {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        justify-content: center;
    }
    .mh-slicer {
        display: flex;
        align-items: center;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 3px;
        gap: 2px;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
    }
    .mh-slicer-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 7px 16px;
        border-radius: 9px;
        font-family: var(--font-body);
        font-size: 13px;
        font-weight: 500;
        color: var(--text-muted);
        text-decoration: none;
        border: 1px solid transparent;
        background: transparent;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
        cursor: pointer;
    }
    .mh-slicer-btn:hover {
        color: var(--text-main);
        background: var(--bg-muted);
    }
    .mh-slicer-btn.active {
        color: var(--text-main);
        background: var(--accent-light);
        border-color: var(--accent);
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .mh-slicer-btn.active .mh-slicer-icon { color: var(--accent); }
    .mh-slicer-icon {
        display: flex;
        align-items: center;
        color: var(--text-faint);
        transition: color 0.2s;
    }
    .mh-right {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1;
        justify-content: flex-end;
        position: relative;
    }
    .mh-account-wrap {
        position: relative;
    }
    .mh-account-trigger {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.16);
        background: linear-gradient(180deg, rgba(59,130,246,0.95) 0%, rgba(37,99,235,0.95) 100%);
        color: #f8fafc;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-family: var(--font-body);
        font-size: 13px;
        font-weight: 700;
        letter-spacing: -0.02em;
        cursor: pointer;
        box-shadow: 0 10px 24px rgba(2,132,199,0.18), inset 0 1px 0 rgba(255,255,255,0.28);
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        padding: 0;
    }
    .mh-account-trigger:hover,
    .mh-account-trigger[aria-expanded="true"] {
        transform: translateY(-1px);
        border-color: rgba(255,255,255,0.28);
        box-shadow: 0 16px 30px rgba(2,132,199,0.22), inset 0 1px 0 rgba(255,255,255,0.32);
    }
    .mh-account-trigger span {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        border-radius: 11px;
        box-shadow: inset 0 0 0 2px rgba(255,255,255,0.82);
    }
    .mh-menu {
        position: absolute;
        top: calc(100% + 10px);
        right: 0;
        width: 232px;
        background: #202536;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        box-shadow: 0 24px 48px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
        padding: 12px 0;
        z-index: 1010;
    }
    .mh-hidden { display: none; }
    .mh-menu-section { padding: 0 14px; }
    .mh-menu-kicker {
        color: var(--text-faint);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .mh-menu-email {
        color: var(--text-main);
        font-family: var(--font-body);
        font-size: 13px;
        font-weight: 600;
        line-height: 1.45;
        word-break: break-word;
        margin-bottom: 4px;
    }
    .mh-menu-divider {
        height: 1px;
        border: 0;
        background: rgba(255,255,255,0.08);
        margin: 12px 0;
    }
    .mh-menu-item {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        background: transparent;
        border: 0;
        color: var(--text-muted);
        text-decoration: none;
        transition: background 0.15s ease, color 0.15s ease;
        font-family: var(--font-body);
        font-size: 13px;
        cursor: pointer;
        text-align: left;
    }
    .mh-menu-item:hover {
        background: rgba(255,255,255,0.04);
        color: var(--text-main);
    }
    .mh-menu-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: rgba(148,163,184,0.72);
        flex-shrink: 0;
    }
    .mh-menu-label { flex: 1; }
    .mh-theme-toggle-row { justify-content: space-between; }
    .mh-theme-switch {
        width: 30px;
        height: 18px;
        border-radius: 999px;
        background: rgba(148,163,184,0.32);
        position: relative;
        transition: background 0.18s ease;
        flex-shrink: 0;
    }
    .mh-theme-switch::after {
        content: "";
        position: absolute;
        top: 2px;
        left: 2px;
        width: 14px;
        height: 14px;
        border-radius: 999px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(15,23,42,0.35);
        transition: transform 0.18s ease;
    }
    .mh-theme-toggle-row[aria-pressed="true"] .mh-theme-switch,
    .mh-theme-switch[data-checked="true"] {
        background: #3b82f6;
    }
    .mh-theme-toggle-row[aria-pressed="true"] .mh-theme-switch::after,
    .mh-theme-switch[data-checked="true"]::after {
        transform: translateX(12px);
    }
    .mh-signout-row { color: #f5b4b4; }
    .mh-signout-row .mh-menu-icon { color: #f87171; }
    .mh-signout-row:hover {
        color: #fee2e2;
        background: rgba(239,68,68,0.08);
    }
    @media (max-width: 780px) {
        .mh-slicer-wrap {
            position: static;
            transform: none;
            order: 3;
            width: 100%;
            justify-content: flex-start;
            margin-top: 10px;
        }
        .module-header {
            height: auto;
            min-height: 60px;
            padding: 12px 18px;
            flex-wrap: wrap;
            gap: 10px 14px;
        }
        .mh-left,
        .mh-right {
            flex: 0 0 auto;
        }
    }
""")


def _user_initials(value):
    if not value:
        return "OD"
    base = str(value).split("@", 1)[0].replace(".", " ").replace("_", " ").replace("-", " ")
    parts = [part for part in base.split() if part]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    compact = "".join(ch for ch in base if ch.isalnum())
    return (compact[:2] or "OD").upper()


def odl_module_header(active_module="catalog", user=None):
    """Renders the top-level module header with the centered module slicer."""
    slicer_btns = []
    for label, href, key, icon_path in MODULES:
        is_active = key == active_module
        slicer_btns.append(
            A(
                Span(icon_svg(icon_path, width="14", height="14"), cls="mh-slicer-icon"),
                label,
                href=href,
                cls=f"mh-slicer-btn {'active' if is_active else ''}",
            )
        )

    left = Div(A("OpenData.London", href="/catalog", cls="mh-brand"), cls="mh-left")
    center = Div(Div(*slicer_btns, cls="mh-slicer"), cls="mh-slicer-wrap")

    right_items = []
    if user:
        right_items.append(
            Div(
                Button(
                    Span(_user_initials(user)),
                    type="button",
                    cls="mh-account-trigger",
                    id="mh-account-trigger",
                    aria_label="Open account menu",
                    aria_expanded="false",
                    aria_controls="mh-account-menu",
                ),
                Div(
                    Div(
                        Div("Logged in as", cls="mh-menu-kicker"),
                        Div(user, cls="mh-menu-email"),
                        cls="mh-menu-section",
                    ),
                    Hr(cls="mh-menu-divider"),
                    Button(
                        Span(icon_svg(IC.moon, width="15", height="15"), cls="mh-menu-icon"),
                        Span("Dark mode", cls="mh-menu-label"),
                        Span(cls="mh-theme-switch", data_theme_indicator="true"),
                        type="button",
                        cls="mh-menu-item mh-theme-toggle-row",
                        data_theme_toggle="true",
                        aria_pressed="true",
                    ),
                    A(
                        Span(icon_svg(IC.info, width="15", height="15"), cls="mh-menu-icon"),
                        Span("About", cls="mh-menu-label"),
                        href="/docs",
                        cls="mh-menu-item",
                    ),
                    A(
                        Span(icon_svg(IC.circle_help, width="15", height="15"), cls="mh-menu-icon"),
                        Span("Help", cls="mh-menu-label"),
                        href="/docs",
                        cls="mh-menu-item",
                    ),
                    A(
                        Span(icon_svg(IC.activity, width="15", height="15"), cls="mh-menu-icon"),
                        Span("Status", cls="mh-menu-label"),
                        href="/usage",
                        cls="mh-menu-item",
                    ),
                    Hr(cls="mh-menu-divider"),
                    A(
                        Span(icon_svg("M10 17l5-5-5-5 M15 12H3 M21 19V5a2 2 0 0 0-2-2h-4", width="15", height="15"), cls="mh-menu-icon"),
                        Span("Sign out", cls="mh-menu-label"),
                        href="/logout",
                        cls="mh-menu-item mh-signout-row",
                    ),
                    id="mh-account-menu",
                    cls="mh-menu mh-hidden",
                    role="menu",
                    aria_label="Account menu",
                ),
                cls="mh-account-wrap",
            )
        )

    right = Div(*right_items, cls="mh-right")

    return Header(
        MODULE_HEADER_STYLE,
        Script("""
document.addEventListener('DOMContentLoaded', function() {
  var trigger = document.getElementById('mh-account-trigger');
  var menu = document.getElementById('mh-account-menu');
  if (!trigger || !menu) return;

  function setOpen(open) {
    menu.classList.toggle('mh-hidden', !open);
    trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  trigger.addEventListener('click', function(event) {
    event.stopPropagation();
    setOpen(menu.classList.contains('mh-hidden'));
  });

  menu.addEventListener('click', function(event) {
    event.stopPropagation();
  });

  document.addEventListener('click', function() {
    setOpen(false);
  });

  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') setOpen(false);
  });
});
"""),
        left,
        center,
        right,
        cls="module-header",
    )
