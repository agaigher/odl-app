from fasthtml.common import *
from app.supabase_db import db_select
from app.components import icon_svg, IC


# ── Role metadata ────────────────────────────────────────────────────────────
ROLES = {
    "owner":         {"label": "Owner",         "bg": "rgba(234,179,8,0.15)",  "fg": "#fcd34d", "border": "rgba(234,179,8,0.3)"},
    "admin":         {"label": "Admin",         "bg": "rgba(56,189,248,0.15)", "fg": "#7dd3fc", "border": "rgba(56,189,248,0.3)"},
    "project_admin": {"label": "Project Admin", "bg": "rgba(16,185,129,0.15)", "fg": "#6ee7b7", "border": "rgba(16,185,129,0.3)"},
    "member":        {"label": "Member",        "bg": "rgba(148,163,184,0.12)","fg": "#94a3b8", "border": "rgba(148,163,184,0.2)"},
}

STATUS_BADGE = {
    "active":  {"label": "Active",  "bg": "rgba(16,185,129,0.15)", "fg": "#6ee7b7", "border": "rgba(16,185,129,0.3)"},
    "pending": {"label": "Pending", "bg": "rgba(234,179,8,0.15)",  "fg": "#fcd34d", "border": "rgba(234,179,8,0.3)"},
}


def _role_badge(role: str):
    r = ROLES.get(role, ROLES["member"])
    return Span(
        r["label"],
        style=f"display:inline-block; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:600; "
              f"letter-spacing:0.04em; text-transform:uppercase; "
              f"background:{r['bg']}; color:{r['fg']}; border:1px solid {r['border']};",
    )


def _status_badge(status: str):
    s = STATUS_BADGE.get(status, STATUS_BADGE["active"])
    return Span(
        s["label"],
        style=f"display:inline-block; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:600; "
              f"letter-spacing:0.04em; text-transform:uppercase; "
              f"background:{s['bg']}; color:{s['fg']}; border:1px solid {s['border']};",
    )


def _team_style():
    return Style("""
        .tm-page { width: 100%; max-width: 1100px; margin: 0 auto; }
        .tm-title {
            font-size: 28px; font-weight: 700; letter-spacing: -0.03em;
            color: #fafafa; margin: 0;
            font-family: 'Space Grotesk', system-ui, sans-serif;
        }
        .tm-sub { font-size: 14px; color: #737373; margin: 4px 0 0 0; }

        .tm-header {
            display: flex; align-items: center; justify-content: space-between;
            flex-wrap: wrap; gap: 16px; margin-bottom: 28px;
        }
        .tm-header-left { display: flex; flex-direction: column; }

        /* Invite button */
        .tm-btn-invite {
            display: inline-flex; align-items: center; gap: 6px;
            background: #0284c7; color: #fff; border: none; font-weight: 600;
            font-size: 14px; padding: 10px 18px; border-radius: 8px; cursor: pointer;
            font-family: 'Inter', sans-serif; white-space: nowrap;
            transition: background 0.15s;
        }
        .tm-btn-invite:hover { background: #0369a1; }

        /* Table wrapper */
        .tm-table-wrap {
            background: #1a1a1a; border: 1px solid #262626; border-radius: 12px;
            overflow: hidden;
        }
        .tm-table { width: 100%; border-collapse: collapse; }
        .tm-table th {
            text-align: left; padding: 14px 18px; font-size: 11px; font-weight: 600;
            color: #525252; text-transform: uppercase; letter-spacing: 0.06em;
            background: #171717; border-bottom: 1px solid #262626;
        }
        .tm-table td {
            padding: 14px 18px; font-size: 14px; color: #e5e5e5;
            border-bottom: 1px solid #1f1f1f; vertical-align: middle;
        }
        .tm-table tr:last-child td { border-bottom: none; }
        .tm-table tr:hover td { background: rgba(255,255,255,0.02); }

        .tm-email { font-weight: 500; color: #fafafa; }
        .tm-meta { font-size: 12px; color: #525252; margin-top: 2px; }

        /* Action buttons */
        .tm-action-btn {
            display: inline-flex; align-items: center; gap: 4px;
            background: transparent; border: 1px solid #333; color: #a3a3a3;
            font-size: 12px; padding: 5px 10px; border-radius: 6px; cursor: pointer;
            font-family: 'Inter', sans-serif; transition: all 0.15s;
        }
        .tm-action-btn:hover { border-color: #525252; color: #e5e5e5; background: #262626; }
        .tm-action-btn.danger { border-color: rgba(239,68,68,0.3); color: #f87171; }
        .tm-action-btn.danger:hover { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.5); }

        /* Inline invite form */
        .tm-invite-form {
            background: #1a1a1a; border: 1px solid #262626; border-radius: 12px;
            padding: 24px; margin-bottom: 24px;
        }
        .tm-invite-form h3 { font-size: 16px; font-weight: 600; color: #fafafa; margin-bottom: 16px; }
        .tm-form-row {
            display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end;
        }
        .tm-form-group { display: flex; flex-direction: column; gap: 6px; }
        .tm-form-group label { font-size: 12px; font-weight: 600; color: #737373; text-transform: uppercase; letter-spacing: 0.06em; }
        .tm-form-input {
            background: #171717; border: 1px solid #333; color: #fafafa;
            padding: 9px 14px; border-radius: 8px; font-size: 14px;
            font-family: 'Inter', sans-serif; outline: none; min-width: 240px;
        }
        .tm-form-input:focus { border-color: #0284c7; }
        .tm-form-input::placeholder { color: #404040; }
        .tm-form-select {
            appearance: none; background: #171717; border: 1px solid #333;
            color: #e5e5e5; font-size: 13px; padding: 9px 32px 9px 14px; border-radius: 8px;
            font-family: 'Inter', sans-serif; cursor: pointer; min-width: 180px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23737373' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
            background-repeat: no-repeat; background-position: right 10px center;
        }
        .tm-btn-send {
            background: #0284c7; color: #fff; border: none; font-weight: 600;
            font-size: 13px; padding: 9px 18px; border-radius: 8px; cursor: pointer;
            font-family: 'Inter', sans-serif;
        }
        .tm-btn-send:hover { background: #0369a1; }

        /* Role change inline select */
        .tm-role-select {
            appearance: none; background: transparent; border: 1px solid #333;
            color: #a3a3a3; font-size: 12px; padding: 4px 24px 4px 8px; border-radius: 6px;
            font-family: 'Inter', sans-serif; cursor: pointer;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%23737373' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
            background-repeat: no-repeat; background-position: right 6px center;
        }

        .tm-empty {
            text-align: center; padding: 48px 24px; color: #525252; font-size: 14px;
        }
        .tm-empty h3 { color: #a3a3a3; font-size: 16px; margin-bottom: 8px; }

        .tm-msg { min-height: 20px; margin-top: 10px; font-size: 13px; }
        .error-text { color: #ef4444; }
        .success-text { color: #10b981; }
    """)


def _member_row(m, viewer_role, org_id, projects_for_org):
    """Render a single member/invite row."""
    email = m.get("invited_email") or m.get("user_id", "Unknown")
    role = m.get("role", "member")
    status = m.get("status", "active")
    member_id = m.get("id", "")
    user_id = m.get("user_id", "")

    # Can viewer manage this member?
    viewer_can_manage = viewer_role in ("owner", "admin")
    is_owner_row = (role == "owner")

    # Role change form (only shown to viewers who can manage, and not on owner rows)
    role_cell = _role_badge(role)
    if viewer_can_manage and not is_owner_row and status == "active":
        available_roles = [("admin", "Admin"), ("project_admin", "Project Admin"), ("member", "Member")]
        if viewer_role == "owner":
            # Only owners can promote to admin
            pass  # admin already in list
        else:
            # Admins can't promote to admin
            available_roles = [("project_admin", "Project Admin"), ("member", "Member")]

        role_cell = Form(
            Select(
                *[Option(label, value=val, selected=(val == role)) for val, label in available_roles],
                name="new_role", cls="tm-role-select",
            ),
            Input(type="hidden", name="membership_id", value=member_id),
            hx_post="/team/role",
            hx_target="#team-table-body",
            hx_trigger="change",
            hx_swap="innerHTML",
            style="display:inline;",
        )

    # Project assignments (for project_admin and member roles)
    project_cell = "All projects" if role in ("owner", "admin") else "—"
    if role in ("project_admin", "member") and status == "active":
        # Look up project_members for this user
        assigned = []
        if user_id and projects_for_org:
            try:
                pm = db_select("project_members", {"user_id": user_id})
                proj_ids = {p["project_id"] for p in pm}
                assigned = [p for p in projects_for_org if p["id"] in proj_ids]
            except Exception:
                assigned = []
        if assigned:
            project_cell = Span(", ".join(p["name"] for p in assigned), style="font-size:13px; color:#a3a3a3;")
        else:
            project_cell = Span("None assigned", style="font-size:12px; color:#525252; font-style:italic;")

    # Status
    status_cell = _status_badge(status)

    # Actions
    actions = []
    if viewer_can_manage and not is_owner_row:
        if status == "pending":
            actions.append(
                Button("Resend", cls="tm-action-btn",
                       hx_post="/team/resend", hx_vals=f'{{"membership_id":"{member_id}"}}',
                       hx_target="#team-table-body", hx_swap="innerHTML")
            )
            actions.append(
                Button("Revoke", cls="tm-action-btn danger",
                       hx_post="/team/revoke", hx_vals=f'{{"membership_id":"{member_id}"}}',
                       hx_target="#team-table-body", hx_swap="innerHTML")
            )
        elif status == "active":
            actions.append(
                Button("Remove", cls="tm-action-btn danger",
                       hx_post="/team/remove", hx_vals=f'{{"membership_id":"{member_id}"}}',
                       hx_target="#team-table-body", hx_swap="innerHTML",
                       hx_confirm=f"Remove {email} from the organization?")
            )

    action_cell = Div(*actions, style="display:flex; gap:6px; flex-wrap:wrap;") if actions else ""

    return Tr(
        Td(
            Div(email, cls="tm-email"),
            Div(f"User ID: {user_id[:8]}..." if user_id else "Invite pending", cls="tm-meta"),
        ),
        Td(role_cell),
        Td(project_cell),
        Td(status_cell),
        Td(action_cell),
    )


def _team_table_body(members, viewer_role, org_id, projects):
    """Just the <tbody> rows — returned by HTMX for partial updates."""
    if not members:
        return Tr(Td("No members found.", colspan="5", cls="tm-empty"))

    # Sort: owner first, then admin, then others; active before pending
    role_order = {"owner": 0, "admin": 1, "project_admin": 2, "member": 3}
    status_order = {"active": 0, "pending": 1}
    members_sorted = sorted(
        members,
        key=lambda m: (role_order.get(m.get("role", "member"), 9), status_order.get(m.get("status", "active"), 9)),
    )
    return [_member_row(m, viewer_role, org_id, projects) for m in members_sorted]


def TeamPage(user_id: str, session: dict):
    style = _team_style()
    active_org_id = session.get("active_org_id") if session else None

    # Resolve active org
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
            H1("Team", cls="tm-title"),
            P("Join or create an organization to manage your team.", cls="tm-sub"),
            Div("You must be part of an organization to manage team members.", cls="tm-empty"),
            cls="tm-page",
        )

    # Fetch org info
    org_name = "Organization"
    try:
        org_rows = db_select("organisations", {"id": active_org_id})
        if org_rows:
            org_name = org_rows[0].get("name", "Organization")
    except Exception:
        pass

    # Fetch all members (active + pending)
    try:
        all_members = db_select("memberships", {"org_id": active_org_id})
    except Exception:
        all_members = []

    # Determine viewer's role
    viewer_role = "member"
    for m in all_members:
        if m.get("user_id") == user_id and m.get("status") == "active":
            viewer_role = m.get("role", "member")
            break

    active_count = sum(1 for m in all_members if m.get("status") == "active")
    pending_count = sum(1 for m in all_members if m.get("status") == "pending")

    # Fetch projects for this org (for project assignment display)
    try:
        projects = db_select("projects", {"org_id": active_org_id})
    except Exception:
        projects = []

    viewer_can_invite = viewer_role in ("owner", "admin")

    # Inline invite form (hidden by default, toggled by JS)
    invite_form = Div(
        H3("Invite a new member"),
        Form(
            Div(
                Div(
                    Label("Email address"),
                    Input(type="email", name="invited_email", required=True,
                          placeholder="colleague@company.com", cls="tm-form-input"),
                    cls="tm-form-group",
                ),
                Div(
                    Label("Role"),
                    Select(
                        Option("Member — view data, use API keys", value="member", selected=True),
                        Option("Project Admin — manage assigned projects", value="project_admin"),
                        Option("Admin — full org management", value="admin"),
                        name="role", cls="tm-form-select",
                    ),
                    cls="tm-form-group",
                ),
                Button("Send Invitation", type="submit", cls="tm-btn-send"),
                cls="tm-form-row",
            ),
            Input(type="hidden", name="org_id", value=active_org_id),
            hx_post="/team/invite",
            hx_target="#invite-msg",
            hx_swap="innerHTML",
        ),
        Div(id="invite-msg", cls="tm-msg"),
        cls="tm-invite-form",
        id="invite-panel",
        style="display:none;",
    ) if viewer_can_invite else ""

    # Header
    header = Div(
        Div(
            H1("Team", cls="tm-title"),
            P(f"{org_name} · {active_count} member{'s' if active_count != 1 else ''}"
              + (f" · {pending_count} pending" if pending_count else ""), cls="tm-sub"),
            cls="tm-header-left",
        ),
        Button(
            Span("+", style="font-size:18px; line-height:1;"),
            " Invite member",
            cls="tm-btn-invite",
            onclick="var p=document.getElementById('invite-panel'); p.style.display=p.style.display==='none'?'block':'none';",
        ) if viewer_can_invite else "",
        cls="tm-header",
    )

    # Members table
    table = Div(
        Table(
            Thead(Tr(
                Th("Member"),
                Th("Role"),
                Th("Projects"),
                Th("Status"),
                Th("Actions"),
            )),
            Tbody(
                *_team_table_body(all_members, viewer_role, active_org_id, projects),
                id="team-table-body",
            ),
            cls="tm-table",
        ),
        cls="tm-table-wrap",
    )

    # Script to reload table body after invite
    reload_script = Script("""
        document.body.addEventListener('htmx:afterSettle', function(evt) {
            if (evt.detail.target && evt.detail.target.id === 'invite-msg') {
                // After invite completes, reload the table body
                setTimeout(function() {
                    htmx.ajax('GET', '/team/members', {target: '#team-table-body', swap: 'innerHTML'});
                }, 600);
            }
        });
    """)

    return Div(
        style,
        header,
        invite_form,
        table,
        reload_script,
        cls="tm-page",
    )
