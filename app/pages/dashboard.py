from fasthtml.common import *
from app.supabase_db import db_select
from datetime import datetime

DASHBOARD_STYLE = Style("""
    .dash-wrap { padding: 32px 40px; max-width: 1100px; }
    .dash-greeting { margin-bottom: 32px; }
    .dash-greeting h1 { font-size: 22px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.3px; }
    .dash-greeting p { font-size: 14px; color: #64748B; margin-top: 4px; }

    .dash-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 40px; }
    .stat-card {
        background: #0F1929; border: 1px solid rgba(148,163,184,0.1);
        border-radius: 10px; padding: 20px 24px;
    }
    .stat-label { font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; }
    .stat-value { font-size: 28px; font-weight: 700; color: #F8FAFC; font-family: 'Roboto Mono', monospace; }

    .dash-section { margin-bottom: 40px; }
    .dash-section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
    .dash-section-title { font-size: 15px; font-weight: 600; color: #F8FAFC; }
    .dash-section-link { font-size: 13px; color: #29b5e8; text-decoration: none; }
    .dash-section-link:hover { text-decoration: underline; }

    .access-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
    .access-card {
        background: #0F1929; border: 1px solid rgba(148,163,184,0.1);
        border-radius: 10px; padding: 18px 20px; text-decoration: none;
        display: flex; flex-direction: column; gap: 10px;
        transition: border-color 0.2s;
    }
    .access-card:hover { border-color: rgba(41,181,232,0.35); }
    .access-card-top { display: flex; align-items: center; justify-content: space-between; }
    .access-card-title { font-size: 14px; font-weight: 600; color: #F8FAFC; line-height: 1.4; }
    .access-card-desc { font-size: 13px; color: #64748B; line-height: 1.5; }
    .access-card-footer { display: flex; gap: 6px; align-items: center; }
    .badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-api { background: rgba(41,181,232,0.12); color: #29b5e8; }
    .badge-sf  { background: rgba(125,211,252,0.08); color: #7DD3FC; }
    .badge-active { background: rgba(16,185,129,0.12); color: #10B981; }
    .badge-pending { background: rgba(245,158,11,0.12); color: #F59E0B; }

    .share-table { width: 100%; border-collapse: collapse; }
    .share-table th { font-size: 11px; font-weight: 600; color: #475569; text-transform: uppercase;
                      letter-spacing: 0.06em; padding: 8px 16px; text-align: left;
                      border-bottom: 1px solid rgba(148,163,184,0.1); }
    .share-table td { font-size: 13px; color: #CBD5E1; padding: 12px 16px;
                      border-bottom: 1px solid rgba(148,163,184,0.06); }
    .share-table tr:last-child td { border-bottom: none; }
    .share-table-wrap { background: #0F1929; border: 1px solid rgba(148,163,184,0.1); border-radius: 10px; overflow: hidden; }

    .org-card {
        background: #0F1929; border: 1px solid rgba(148,163,184,0.1);
        border-radius: 10px; padding: 20px 24px;
        display: flex; align-items: center; justify-content: space-between;
        text-decoration: none; transition: border-color 0.2s;
        max-width: 480px;
    }
    .org-card:hover { border-color: rgba(41,181,232,0.35); }
    .org-card-left h3 { font-size: 15px; font-weight: 600; color: #F8FAFC; margin-bottom: 4px; }
    .org-card-left p { font-size: 13px; color: #64748B; }
    .org-card-arrow { color: #475569; font-size: 18px; }

    .empty-state {
        background: #0F1929; border: 1px solid rgba(148,163,184,0.08);
        border-radius: 12px; padding: 48px 32px; text-align: center;
    }
    .empty-state h2 { font-size: 17px; font-weight: 600; color: #F8FAFC; margin-bottom: 8px; }
    .empty-state p { font-size: 14px; color: #64748B; line-height: 1.6; margin-bottom: 24px; }
    .btn-primary {
        display: inline-block; background: #29b5e8; color: #0B1120;
        font-weight: 600; font-size: 14px; padding: 10px 22px;
        border-radius: 6px; text-decoration: none; transition: opacity 0.2s;
    }
    .btn-primary:hover { opacity: 0.88; }
    .btn-secondary {
        display: inline-block; background: transparent;
        border: 1px solid rgba(148,163,184,0.2); color: #CBD5E1;
        font-weight: 500; font-size: 14px; padding: 10px 22px;
        border-radius: 6px; text-decoration: none; transition: border-color 0.2s;
        margin-left: 10px;
    }
    .btn-secondary:hover { border-color: rgba(148,163,184,0.4); }
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
        Div(Span(ds.get("provider") or "", style="font-size: 12px; color: #475569;"), cls="access-card-footer"),
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
        Td(req.get("snowflake_account", ""), style="font-family: 'Roboto Mono', monospace; font-size: 12px;"),
        Td(status_badge),
        Td(days_ago, style="color: #475569;"),
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
            P("You are not part of any organisation.", style="color: #64748B; font-size: 14px; margin-bottom: 14px;"),
            A("Create an organisation", href="/create-org", cls="btn-secondary", style="margin-left: 0;"),
            style="padding: 24px; background: #0F1929; border: 1px solid rgba(148,163,184,0.1); border-radius: 10px;"
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
            P(datetime.utcnow().strftime("%A, %d %B %Y"), style="color: #475569;"),
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
