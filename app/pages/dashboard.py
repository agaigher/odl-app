from fasthtml.common import *
from app.supabase_db import db_select
from datetime import datetime

DASHBOARD_STYLE = Style("""
    /* Dark surfaces — same family as app shell (no harsh white cards on #080a0f) */
    .dash-wrap { max-width: 1100px; }
    .dash-greeting { margin-bottom: 28px; }
    .dash-greeting h1 { font-size: 22px; font-weight: 600; color: #F8FAFC; letter-spacing: -0.03em; }
    .dash-greeting p { font-size: 14px; color: #94A3B8; margin-top: 4px; }

    .dash-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 36px; }
    .stat-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 18px 20px;
        box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset;
    }
    .stat-label { font-size: 10px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }
    .stat-value { font-size: 26px; font-weight: 600; color: #F1F5F9; font-family: 'JetBrains Mono', 'Roboto Mono', ui-monospace, monospace; letter-spacing: -0.02em; }

    .dash-section { margin-bottom: 36px; }
    .dash-section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
    .dash-section-title { font-size: 14px; font-weight: 600; color: #CBD5E1; letter-spacing: -0.01em; }
    .dash-section-link { font-size: 13px; color: #38bdf8; text-decoration: none; font-weight: 500; }
    .dash-section-link:hover { color: #7dd3fc; text-decoration: underline; }

    .access-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
    .access-card {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 18px 20px; text-decoration: none;
        display: flex; flex-direction: column; gap: 10px;
        transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
        box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset;
    }
    .access-card:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.08);
    }
    .access-card-top { display: flex; align-items: center; justify-content: space-between; }
    .access-card-title { font-size: 14px; font-weight: 600; color: #F1F5F9; line-height: 1.4; }
    .access-card-desc { font-size: 13px; color: #94A3B8; line-height: 1.5; }
    .access-card-footer { display: flex; gap: 6px; align-items: center; }
    .badge { padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
    .badge-api     { background: rgba(2, 132, 199, 0.2); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.2); }
    .badge-sf      { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.2); }
    .badge-active  { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.2); }
    .badge-pending { background: rgba(234, 179, 8, 0.12); color: #fcd34d; border: 1px solid rgba(234, 179, 8, 0.2); }

    .share-table { width: 100%; border-collapse: collapse; }
    .share-table th { font-size: 10px; font-weight: 600; color: #64748B; text-transform: uppercase;
                      letter-spacing: 0.08em; padding: 10px 16px; text-align: left;
                      border-bottom: 1px solid rgba(255,255,255,0.06); background: rgba(0,0,0,0.2); }
    .share-table td { font-size: 13px; color: #E2E8F0; padding: 12px 16px;
                      border-bottom: 1px solid rgba(255,255,255,0.05); }
    .share-table tr:last-child td { border-bottom: none; }
    .share-table-wrap {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; overflow: hidden;
        box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset;
    }

    .org-card {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 18px 22px;
        display: flex; align-items: center; justify-content: space-between;
        text-decoration: none; transition: border-color 0.2s, background 0.2s;
        max-width: 480px;
    }
    .org-card:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(56, 189, 248, 0.22);
    }
    .org-card-left h3 { font-size: 15px; font-weight: 600; color: #F1F5F9; margin-bottom: 4px; }
    .org-card-left p { font-size: 13px; color: #94A3B8; }
    .org-card-arrow { color: #64748B; font-size: 18px; }

    .empty-state {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 48px 32px; text-align: center;
    }
    .empty-state h2 { font-size: 17px; font-weight: 600; color: #F1F5F9; margin-bottom: 8px; }
    .empty-state p { font-size: 14px; color: #94A3B8; line-height: 1.6; margin-bottom: 24px; max-width: 440px; margin-left: auto; margin-right: auto; white-space: pre-line; }
    .btn-primary {
        display: inline-block; background: #0284C7; color: #ffffff;
        font-weight: 500; font-size: 14px; padding: 10px 22px;
        border-radius: 8px; text-decoration: none; transition: background 0.2s;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .btn-primary:hover { background: #0369A1; }
    .btn-secondary {
        display: inline-block; background: transparent;
        border: 1px solid rgba(255,255,255,0.14); color: #CBD5E1;
        font-weight: 500; font-size: 14px; padding: 10px 22px;
        border-radius: 8px; text-decoration: none; transition: border-color 0.2s, color 0.2s, background 0.2s;
        margin-left: 10px;
    }
    .btn-secondary:hover { border-color: rgba(255,255,255,0.28); color: #F8FAFC; background: rgba(255,255,255,0.05); }
""")


def _greeting():
    h = datetime.utcnow().hour
    if h < 12:   return "Good morning"
    if h < 18:   return "Good afternoon"
    return "Good evening"


def _access_card(ds):
    access_type = ds.get("access_type", "api")
    status = ds.get("access_status", "active")
    type_badge = Span("API", cls="badge badge-api") if access_type == "api" else Span("Snowflake", cls="badge badge-sf")
    status_badge = Span("Active", cls="badge badge-active") if status == "active" else Span("Pending", cls="badge badge-pending")
    return A(
        Div(type_badge, status_badge, cls="access-card-top"),
        P(ds.get("title") or ds.get("dataset_slug", ""), cls="access-card-title"),
        P(ds.get("description") or "", cls="access-card-desc"),
        Div(Span(ds.get("provider") or "", style="font-size: 12px; color: #94A3B8;"), cls="access-card-footer"),
        href=f"/catalog/{ds.get('slug', ds.get('dataset_slug', ''))}",
        cls="access-card"
    )


def _share_row(req):
    days_ago = ""
    if req.get("requested_at"):
        try:
            dt = datetime.fromisoformat(req["requested_at"].replace("Z", "+00:00"))
            delta = (datetime.now(dt.tzinfo) - dt).days
            days_ago = f"{delta}d ago" if delta > 0 else "Today"
        except Exception:
            pass
    status = req.get("status", "pending")
    status_badge = Span("Pending", cls="badge badge-pending") if status == "pending" else Span("Fulfilled", cls="badge badge-active")
    return Tr(
        Td(req.get("dataset_slug", "").replace("-", " ").title()),
        Td(req.get("snowflake_account", ""), style="font-family: 'JetBrains Mono', 'Roboto Mono', monospace; font-size: 12px; color: #CBD5E1;"),
        Td(status_badge),
        Td(days_ago, style="color: #94A3B8;"),
    )


def Dashboard(user_id: str, user_email: str):
    # ── Fetch data ────────────────────────────────────────────────────────────
    try:
        accesses = db_select("dataset_access", {"user_id": user_id})
    except Exception:
        accesses = []

    try:
        share_reqs = db_select("share_requests", {"user_id": user_id})
    except Exception:
        share_reqs = []

    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
    except Exception:
        memberships = []

    orgs = []
    for m in memberships:
        try:
            org_rows = db_select("organisations", {"id": m["org_id"]})
            if org_rows:
                all_members = db_select("memberships", {"org_id": m["org_id"], "status": "active"})
                orgs.append({**org_rows[0], "role": m["role"], "member_count": len(all_members)})
        except Exception:
            pass

    # Enrich accesses with dataset metadata
    datasets_with_access = []
    for a in accesses:
        try:
            ds_rows = db_select("datasets", {"slug": a["dataset_slug"]})
            if ds_rows:
                datasets_with_access.append({**ds_rows[0], "access_type": a["access_type"], "access_status": a["status"]})
            else:
                datasets_with_access.append({"dataset_slug": a["dataset_slug"], "access_type": a["access_type"], "access_status": a["status"]})
        except Exception:
            pass

    pending_shares = [s for s in share_reqs if s.get("status") == "pending"]
    is_empty = not datasets_with_access and not pending_shares and not orgs

    # ── Stats ─────────────────────────────────────────────────────────────────
    total_members = sum(o.get("member_count", 0) for o in orgs) if orgs else 0
    stats = [
        ("Datasets", len(datasets_with_access)),
        ("Pending shares", len(pending_shares)),
        ("API keys", 0),
        ("Org members", total_members),
    ]

    name = user_email.split("@")[0].replace(".", " ").title()

    # ── Sections ──────────────────────────────────────────────────────────────
    datasets_section = Div(
        Div(
            Span("Your datasets", cls="dash-section-title"),
            A("Browse catalog →", href="/catalog", cls="dash-section-link"),
            cls="dash-section-header"
        ),
        Div(*[_access_card(ds) for ds in datasets_with_access], cls="access-grid"),
        cls="dash-section"
    ) if datasets_with_access else None

    shares_section = Div(
        Div(Span("Snowflake share requests", cls="dash-section-title"), cls="dash-section-header"),
        Div(
            Table(
                Thead(Tr(Th("Dataset"), Th("Snowflake account"), Th("Status"), Th("Requested"))),
                Tbody(*[_share_row(r) for r in share_reqs]),
                cls="share-table"
            ),
            cls="share-table-wrap"
        ),
        cls="dash-section"
    ) if share_reqs else None

    org_section = Div(
        Div(Span("Organisation", cls="dash-section-title"), cls="dash-section-header"),
        Div(*[
            A(
                Div(
                    H3(o["name"]),
                    P(f"{o['role'].title()} · {o['member_count']} member{'s' if o['member_count'] != 1 else ''}"),
                    cls="org-card-left"
                ),
                Span("→", cls="org-card-arrow"),
                href=f"/org/{o['slug']}",
                cls="org-card"
            )
            for o in orgs
        ], style="display: flex; flex-direction: column; gap: 12px;"),
        cls="dash-section"
    ) if orgs else Div(
        Div(Span("Organisation", cls="dash-section-title"), cls="dash-section-header"),
        Div(
            P("You are not part of any organisation.", style="color: #94A3B8; font-size: 14px; margin-bottom: 14px;"),
            A("Create an organisation", href="/create-org", cls="btn-secondary", style="margin-left: 0;"),
            style="padding: 24px; background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;"
        ),
        cls="dash-section"
    )

    empty_state = Div(
        H2("Welcome to OpenData.London"),
        P("Browse the London Database and request access to the datasets you need.\nYour active datasets, API keys, and Snowflake shares will appear here."),
        A("Browse the catalog", href="/catalog", cls="btn-primary"),
        A("Create an organisation", href="/create-org", cls="btn-secondary"),
        cls="empty-state"
    ) if is_empty else None

    return Div(
        DASHBOARD_STYLE,
        Div(
            H1(f"{_greeting()}, {name}"),
            P(datetime.utcnow().strftime("%A, %d %B %Y"), style="color: #94A3B8;"),
            cls="dash-greeting"
        ),
        Div(*[
            Div(
                P(label, cls="stat-label"),
                P(str(value), cls="stat-value"),
                cls="stat-card"
            )
            for label, value in stats
        ], cls="dash-stats"),
        empty_state or Div(datasets_section, shares_section, org_section),
        cls="dash-wrap"
    )
