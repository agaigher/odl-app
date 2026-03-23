from fasthtml.common import *
from app.supabase_db import db_select
from app.components import icon_svg, IC


def _projects_style():
    """Projects dashboard — dark shell, toolbar, grid cards (reference UI)."""
    return Style("""
        .pd-page { width: 100%; max-width: 1280px; margin: 0 auto; }
        .pd-title {
            font-size: 32px; font-weight: 600; letter-spacing: -0.03em;
            color: #fafafa; margin: 0 0 6px 0;
            font-family: 'Space Grotesk', system-ui, sans-serif;
        }
        .pd-sub { font-size: 14px; color: #737373; margin: 0 0 28px 0; }

        .pd-toolbar {
            display: flex; flex-wrap: wrap; align-items: center; gap: 12px 16px;
            margin-bottom: 28px;
        }
        .pd-search-wrap {
            flex: 1 1 220px; min-width: 200px; max-width: 420px;
            display: flex; align-items: center; gap: 10px;
            background: #171717; border: 1px solid #262626; border-radius: 8px;
            padding: 0 12px 0 14px; height: 40px; box-sizing: border-box;
        }
        .pd-search-wrap svg { flex-shrink: 0; color: #525252; }
        .pd-search-wrap input {
            flex: 1; min-width: 0; background: transparent; border: none; outline: none;
            color: #fafafa; font-size: 14px; font-family: 'Inter', sans-serif;
        }
        .pd-search-wrap input::placeholder { color: #525252; }

        .pd-toolbar-mid {
            display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
        }
        .pd-select {
            appearance: none; background: #171717; border: 1px solid #262626;
            color: #e5e5e5; font-size: 13px; padding: 8px 32px 8px 12px; border-radius: 8px;
            font-family: 'Inter', sans-serif; cursor: pointer;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23737373' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
            background-repeat: no-repeat; background-position: right 10px center;
        }
        .pd-sort-btn {
            display: inline-flex; align-items: center; gap: 8px;
            background: #171717; border: 1px solid #262626; color: #e5e5e5;
            font-size: 13px; padding: 8px 14px; border-radius: 8px; cursor: pointer;
            font-family: 'Inter', sans-serif;
        }
        .pd-sort-btn:hover { border-color: #404040; }

        .pd-toolbar-right {
            display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
            margin-left: auto;
        }
        .pd-view-toggle {
            display: flex; border: 1px solid #262626; border-radius: 8px; overflow: hidden;
            background: #171717;
        }
        .pd-view-btn {
            width: 40px; height: 38px; display: flex; align-items: center; justify-content: center;
            background: transparent; border: none; color: #737373; cursor: pointer;
            padding: 0;
        }
        .pd-view-btn:hover { color: #a3a3a3; }
        .pd-view-btn.is-active {
            background: #262626; color: #fafafa;
            box-shadow: inset 0 0 0 1px #404040;
        }
        .pd-view-btn + .pd-view-btn { border-left: 1px solid #262626; }

        .pd-new-form { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .pd-new-name {
            width: 140px; background: #171717; border: 1px solid #262626; color: #fafafa;
            padding: 8px 12px; border-radius: 8px; font-size: 13px; font-family: 'Inter', sans-serif;
            outline: none;
        }
        .pd-new-name:focus { border-color: #404040; }
        .pd-new-name::placeholder { color: #525252; }
        .pd-btn-new {
            display: inline-flex; align-items: center; gap: 6px;
            background: #00875a; color: #fff; border: none; font-weight: 600;
            font-size: 14px; padding: 10px 16px; border-radius: 8px; cursor: pointer;
            font-family: 'Inter', sans-serif; white-space: nowrap;
        }
        .pd-btn-new:hover { background: #006b47; }

        .pd-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .pd-grid.pd-grid--list {
            grid-template-columns: 1fr;
        }
        .pd-grid.pd-grid--list .pd-card { flex-direction: row; align-items: stretch; }
        .pd-grid.pd-grid--list .pd-card-main { flex: 1; }

        .pd-card {
            background: #1a1a1a; border: 1px solid #262626; border-radius: 12px;
            padding: 20px; display: flex; flex-direction: column; min-height: 160px;
            transition: border-color 0.15s ease;
        }
        .pd-card:hover { border-color: #404040; }

        .pd-card-head {
            display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
            margin-bottom: 8px;
        }
        .pd-card-title {
            font-size: 16px; font-weight: 600; color: #fafafa; text-decoration: none;
            font-family: 'Inter', sans-serif; letter-spacing: -0.02em; line-height: 1.3;
        }
        .pd-card-title:hover { color: #fff; }
        .pd-card-kebab {
            flex-shrink: 0; width: 32px; height: 32px; border: none; border-radius: 6px;
            background: transparent; color: #737373; cursor: pointer; font-size: 18px;
            line-height: 1; padding: 0; display: flex; align-items: center; justify-content: center;
        }
        .pd-card-kebab:hover { background: #262626; color: #a3a3a3; }

        .pd-card-meta {
            font-size: 13px; color: #737373; margin-bottom: 16px;
            font-family: 'Inter', sans-serif;
        }
        .pd-card-badges { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: auto; }
        .pd-badge {
            font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
            padding: 4px 10px; border-radius: 999px; font-family: 'Inter', sans-serif;
        }
        .pd-badge--active { background: rgba(0, 135, 90, 0.2); color: #34d399; border: 1px solid rgba(0, 135, 90, 0.35); }
        .pd-badge--muted { background: #262626; color: #a3a3a3; border: 1px solid #404040; }
        .pd-badge--nano { background: #262626; color: #737373; border: 1px solid #404040; }

        .pd-card-alert {
            margin-top: 16px; padding: 12px 14px; border-radius: 8px;
            background: #171717; border: 1px solid #262626;
            display: flex; align-items: center; gap: 10px; font-size: 13px; color: #a3a3a3;
        }
        .pd-card-alert svg { flex-shrink: 0; color: #737373; }

        .pd-empty {
            grid-column: 1 / -1; text-align: center; padding: 64px 24px;
            border: 1px dashed #333; border-radius: 12px; background: #141414; color: #737373;
            font-size: 14px;
        }
        .pd-empty h3 { color: #e5e5e5; font-size: 16px; margin: 0 0 8px 0; }

        .pd-error {
            padding: 20px; border-radius: 12px; background: #1a1a1a; border: 1px solid #333;
            color: #a3a3a3; font-size: 14px;
        }
    """)


def _projects_script():
    return Script("""
(function () {
  function init() {
    var grid = document.getElementById('pd-project-grid');
    if (!grid) return;
    var search = document.getElementById('pd-search');
    var status = document.getElementById('pd-status-filter');
    var sortBtn = document.getElementById('pd-sort-btn');
    var btnGrid = document.getElementById('pd-view-grid');
    var btnList = document.getElementById('pd-view-list');
    var sortAsc = true;

    function visibleCards() {
      return Array.prototype.slice.call(grid.querySelectorAll('.pd-card'));
    }

    function apply() {
      var q = (search && search.value ? search.value : '').toLowerCase().trim();
      var st = status ? status.value : 'all';
      var cards = visibleCards();
      cards.forEach(function (c) {
        var name = (c.getAttribute('data-name') || '').toLowerCase();
        var ps = c.getAttribute('data-status') || '';
        var okName = !q || name.indexOf(q) !== -1;
        var okSt = st === 'all' || ps === st;
        c.style.display = (okName && okSt) ? '' : 'none';
      });
      var shown = cards.filter(function (c) { return c.style.display !== 'none'; });
      shown.sort(function (a, b) {
        var na = a.getAttribute('data-name') || '';
        var nb = b.getAttribute('data-name') || '';
        return sortAsc ? na.localeCompare(nb) : nb.localeCompare(na);
      });
      shown.forEach(function (c) { grid.appendChild(c); });
    }

    if (search) search.addEventListener('input', apply);
    if (status) status.addEventListener('change', apply);
    if (sortBtn) {
      sortBtn.addEventListener('click', function () {
        sortAsc = !sortAsc;
        apply();
      });
    }
    if (btnGrid && btnList) {
      btnGrid.addEventListener('click', function () {
        grid.classList.remove('pd-grid--list');
        btnGrid.classList.add('is-active');
        btnList.classList.remove('is-active');
      });
      btnList.addEventListener('click', function () {
        grid.classList.add('pd-grid--list');
        btnList.classList.add('is-active');
        btnGrid.classList.remove('is-active');
      });
    }
  }
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', init);
  else
    init();
})();
""")


# Pause icon (rectangle with two bars) for "project paused" strip
_PD_PAUSE_SVG = (
    "M8 5v14M16 5v14M5 5h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"
)


def _project_card(p, org_label: str, is_active_project: bool):
    """Card layout aligned with reference: meta line, badges, optional paused footer."""
    name = (p.get("name") or "Untitled").strip()
    pid = p.get("id", "")
    href = f"/projects/{pid}/select"

    # Display line similar to "AWS | eu-west-1" — we use org + a fixed region label until infra metadata exists.
    meta_line = f"{org_label} | EU West (London)"

    badges = []
    if is_active_project:
        badges.append(Span("Active", cls="pd-badge pd-badge--active"))
        badges.append(Span("Default", cls="pd-badge pd-badge--nano"))
    else:
        badges.append(Span("Paused", cls="pd-badge pd-badge--muted"))

    paused_footer = None
    if not is_active_project:
        paused_footer = Div(
            icon_svg(_PD_PAUSE_SVG, width="16", height="16"),
            Span("Project is paused"),
            icon_svg(IC.info, width="16", height="16"),
            cls="pd-card-alert",
        )

    slug = name.lower()

    return Div(
        Div(
            A(name, href=href, cls="pd-card-title"),
            Button("⋮", type="button", cls="pd-card-kebab", aria_label="Project actions"),
            cls="pd-card-head",
        ),
        A(
            Div(meta_line, cls="pd-card-meta"),
            Div(*badges, cls="pd-card-badges"),
            href=href,
            cls="pd-card-main",
            style="text-decoration: none; color: inherit; display: block;",
        ),
        paused_footer,
        cls="pd-card",
        data_name=slug,
        data_status="active" if is_active_project else "paused",
    )


def ProjectsDashboard(user_id="", session=None):
    style = _projects_style()
    script = _projects_script()

    active_org_id = session.get("active_org_id") if session else None

    if not active_org_id:
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if memberships:
                active_org_id = memberships[0]["org_id"]
                if session:
                    session["active_org_id"] = active_org_id
        except Exception:
            pass

    if not active_org_id:
        return Div(
            style,
            script,
            H1("Projects", cls="pd-title"),
            P("Join or create an organization to manage projects.", cls="pd-sub"),
            Div("You must be part of an organization to create projects.", cls="pd-error"),
            cls="pd-page",
        )

    try:
        projects = db_select("projects", {"org_id": active_org_id})
    except Exception:
        projects = []

    org_row = None
    try:
        org_rows = db_select("organisations", {"id": active_org_id})
        if org_rows:
            org_row = org_rows[0]
    except Exception:
        pass

    org_label = (org_row.get("name") or "Workspace").strip()
    active_project_id = session.get("active_project_id") if session else None

    new_form = Form(
        Input(
            type="text",
            name="name",
            placeholder="Name",
            required=True,
            cls="pd-new-name",
            aria_label="New project name",
        ),
        Input(type="hidden", name="org_id", value=active_org_id),
        Button(
            Span("+", style="font-size: 18px; line-height: 1;"),
            " New project",
            type="submit",
            cls="pd-btn-new",
        ),
        hx_post="/projects/create",
        hx_on__after_request="if(event.detail.successful) window.location.reload()",
        cls="pd-new-form",
    )

    toolbar = Div(
        Div(
            icon_svg(IC.search, width="18", height="18"),
            Input(
                type="search",
                id="pd-search",
                placeholder="Search for a project",
                cls="pd-search-input",
                style="border:none;outline:none;background:transparent;flex:1;color:#fafafa;font-size:14px;",
            ),
            cls="pd-search-wrap",
        ),
        Div(
            Select(
                Option("All statuses", value="all"),
                Option("Active", value="active"),
                Option("Paused", value="paused"),
                id="pd-status-filter",
                cls="pd-select",
            ),
            Button(
                icon_svg("M4 6h16M8 12h12M11 18h8", width="16", height="16"),
                " Sorted by name",
                id="pd-sort-btn",
                type="button",
                cls="pd-sort-btn",
            ),
            cls="pd-toolbar-mid",
        ),
        Div(
            Div(
                Button(
                    icon_svg(IC.grid, width="18", height="18"),
                    type="button",
                    cls="pd-view-btn is-active",
                    id="pd-view-grid",
                    aria_label="Grid view",
                ),
                Button(
                    icon_svg("M8 6h13M8 12h13M8 18h13M4 6h.01M4 12h.01M4 18h.01", width="18", height="18"),
                    type="button",
                    cls="pd-view-btn",
                    id="pd-view-list",
                    aria_label="List view",
                ),
                cls="pd-view-toggle",
            ),
            new_form,
            cls="pd-toolbar-right",
        ),
        cls="pd-toolbar",
    )

    cards = [
        _project_card(
            p,
            org_label,
            str(p.get("id")) == str(active_project_id),
        )
        for p in (projects or [])
    ]

    empty = Div(
        H3("No projects yet"),
        P("Create a project to organize API keys, shares, and access for ", org_label, "."),
        cls="pd-empty",
    )

    grid_el = (
        Div(*cards, id="pd-project-grid", cls="pd-grid")
        if projects
        else Div(empty, id="pd-project-grid", cls="pd-grid")
    )

    return Div(
        style,
        script,
        H1("Projects", cls="pd-title"),
        P(f"Organization · {org_label}", cls="pd-sub"),
        toolbar,
        grid_el,
        cls="pd-page",
    )
