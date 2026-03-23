from fasthtml.common import *
from app.supabase_db import db_select
from app.components import icon_svg, IC


def _projects_style():
    """Match organisations.py — same layout tokens and card system."""
    return Style("""
        .projects-container { width: 100%; }
        .projects-header {
            display: flex; justify-content: space-between; align-items: flex-start;
            flex-wrap: wrap; gap: 20px; margin-bottom: 32px;
        }
        .projects-header-text h1 {
            font-size: 24px; font-weight: 700; color: #F8FAFC; margin: 0;
        }
        .projects-header-text p {
            color: #94A3B8; font-size: 14px; margin-top: 4px; max-width: 520px;
        }
        .projects-new-form {
            display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
        }
        .projects-new-form input[type="text"] {
            min-width: 220px; background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.1); color: #F8FAFC;
            padding: 10px 14px; border-radius: 8px; font-size: 14px;
            font-family: 'Inter', sans-serif; outline: none;
        }
        .projects-new-form input[type="text"]:focus {
            border-color: rgba(56,189,248,0.35); box-shadow: 0 0 0 1px rgba(2,132,199,0.12);
        }
        .projects-new-form input::placeholder { color: #64748B; }
        .projects-create-btn {
            background: #0284C7; color: #ffffff; border: none;
            padding: 10px 18px; border-radius: 8px; font-weight: 600; font-size: 14px;
            cursor: pointer; font-family: 'Inter', sans-serif;
            display: inline-flex; align-items: center; gap: 8px;
            transition: background 0.2s;
        }
        .projects-create-btn:hover { background: #0369A1; }

        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
        }

        .proj-card {
            background: #1E293B; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;
            padding: 24px; transition: all 0.2s; text-decoration: none;
            display: flex; flex-direction: column; cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .proj-card:hover {
            border-color: #0284C7; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
            transform: translateY(-2px);
        }
        .proj-logo-large {
            width: 48px; height: 48px; border-radius: 8px;
            background: #0F172A; border: 1px solid rgba(255,255,255,0.05);
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 16px; font-weight: 700; color: #94A3B8; font-size: 20px;
        }
        .proj-name {
            font-size: 18px; font-weight: 700; color: #F8FAFC; margin-bottom: 4px;
        }
        .proj-meta {
            font-size: 13px; color: #94A3B8; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
        }
        .proj-id-badge {
            font-size: 10px; font-weight: 700; background: #0F172A;
            color: #94A3B8; padding: 2px 6px; border-radius: 4px;
            text-transform: uppercase; letter-spacing: 0.04em;
        }
        .proj-action-bar {
            margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.05);
            display: flex; justify-content: flex-end;
        }
        .proj-open-btn { font-size: 13px; font-weight: 600; color: #0284C7; display: flex; align-items: center; gap: 4px; }

        .projects-empty {
            grid-column: 1 / -1; text-align: center; padding: 80px 20px;
            border: 2px dashed rgba(255,255,255,0.05); border-radius: 12px; background: #1E293B;
        }
        .projects-empty h3 { font-size: 16px; font-weight: 600; color: #F8FAFC; margin: 0; }
        .projects-empty p { color: #94A3B8; font-size: 14px; margin-top: 8px; }

        .projects-error {
            padding: 24px; border-radius: 12px; background: #1E293B;
            border: 1px solid rgba(255,255,255,0.06); color: #94A3B8; font-size: 14px;
        }

        /* Org summary — same family as dashboard stat cards */
        .proj-org-strip {
            margin-bottom: 28px;
            padding: 20px 22px;
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset;
        }
        .proj-org-strip-inner {
            display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: space-between; gap: 20px;
        }
        .proj-org-kicker {
            font-size: 10px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em;
            display: block; margin-bottom: 6px;
        }
        .proj-org-title { font-size: 18px; font-weight: 600; color: #F8FAFC; margin: 0; letter-spacing: -0.02em; }
        .proj-org-stats {
            display: flex; flex-wrap: wrap; gap: 12px;
        }
        .proj-mini-stat {
            background: rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 12px 18px;
            min-width: 100px;
        }
        .proj-mini-stat-label {
            font-size: 10px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;
            margin: 0 0 8px 0;
        }
        .proj-mini-stat-value {
            font-size: 22px; font-weight: 600; color: #F1F5F9;
            margin: 0;
            font-family: 'JetBrains Mono', ui-monospace, monospace;
            letter-spacing: -0.02em;
        }
    """)


def _project_card(p, is_active):
    name = p.get("name") or "Untitled"
    pid = p.get("id", "")
    pid_short = f"{str(pid)[:8]}…" if pid else "—"
    meta_bits = [
        Span("Project", cls="proj-id-badge"),
        Span("•"),
        Span(
            f"ID {pid_short}",
            style="font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 12px;",
        ),
    ]
    if is_active:
        meta_bits.extend([Span("•"), Span("Active", style="color: #10B981;")])
    return A(
        Div(name[0].upper(), cls="proj-logo-large"),
        Div(name, cls="proj-name"),
        Div(*meta_bits, cls="proj-meta"),
        Div(Span("Open project overview", cls="proj-open-btn"), cls="proj-action-bar"),
        href=f"/projects/{p['id']}/select",
        cls="proj-card",
    )


def ProjectsDashboard(user_id="", session=None):
    style = _projects_style()

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
            Div(
                Div(
                    H1("Projects"),
                    P("Projects belong to an organization. Join or create one to continue."),
                    cls="projects-header-text",
                ),
                cls="projects-header",
            ),
            Div(
                "You must be part of an organization to create projects.",
                cls="projects-error",
            ),
            cls="projects-container",
        )

    try:
        projects = db_select("projects", {"org_id": active_org_id})
    except Exception:
        projects = []

    org_row = None
    member_count = 0
    try:
        org_rows = db_select("organisations", {"id": active_org_id})
        if org_rows:
            org_row = org_rows[0]
        members = db_select("memberships", {"org_id": active_org_id, "status": "active"})
        member_count = len(members or [])
    except Exception:
        pass

    project_count = len(projects or [])
    active_project_id = session.get("active_project_id") if session else None

    org_strip = None
    if org_row:
        org_strip = Div(
            Div(
                Div(
                    Span("Active organization", cls="proj-org-kicker"),
                    H2(org_row.get("name") or "Organization", cls="proj-org-title"),
                ),
                Div(
                    Div(
                        P("Projects", cls="proj-mini-stat-label"),
                        P(str(project_count), cls="proj-mini-stat-value"),
                        cls="proj-mini-stat",
                    ),
                    Div(
                        P("Members", cls="proj-mini-stat-label"),
                        P(str(member_count), cls="proj-mini-stat-value"),
                        cls="proj-mini-stat",
                    ),
                    cls="proj-org-stats",
                ),
                cls="proj-org-strip-inner",
            ),
            cls="proj-org-strip",
        )

    new_proj_form = Form(
        Input(
            type="text",
            name="name",
            placeholder="New project name…",
            required=True,
        ),
        Input(type="hidden", name="org_id", value=active_org_id),
        Button(
            icon_svg(IC.plus_circle, style="width: 16px; height: 16px;"),
            "New project",
            type="submit",
            cls="projects-create-btn",
        ),
        hx_post="/projects/create",
        hx_on__after_request="if(event.detail.successful) window.location.reload()",
        cls="projects-new-form",
    )

    cards = [_project_card(p, str(p["id"]) == str(active_project_id)) for p in projects]

    empty = Div(
        Div(icon_svg(IC.box, style="width: 48px; height: 48px; color: #64748B; margin: 0 auto 16px;")),
        H3("No projects yet"),
        P("Create a project to organize integrations, API keys, and data access for this organization."),
        cls="projects-empty",
    )

    grid_content = Div(*cards, cls="projects-grid") if projects else Div(empty, cls="projects-grid")

    body_children = [
        Div(
            Div(
                H1("Projects"),
                P("Manage multiple environments and API access within this organization."),
                cls="projects-header-text",
            ),
            new_proj_form,
            cls="projects-header",
        ),
    ]
    if org_strip:
        body_children.append(org_strip)
    body_children.append(grid_content)

    return Div(
        style,
        *body_children,
        cls="projects-container",
    )
