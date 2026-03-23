from fasthtml.common import *
from app.supabase_db import db_select


def OrgDashboard(org):
    try:
        from app.supabase_db import db_select
        members = db_select("memberships", {"org_id": org["id"]})
    except Exception as e:
        return Div(f"Error loading organisation: {str(e)}", style="color: #EF4444;")

    member_rows = []
    for m in members:
        email = m.get("invited_email") or m.get("user_id", "—")
        role = m.get("role", "member")
        status = m.get("status", "active")
        role_badge_color = "#29b5e8" if role == "admin" else "#64748B"
        status_color = "#10B981" if status == "active" else "#F59E0B"
        member_rows.append(
            Tr(
                Td(email, style="padding: 12px 16px; color: #E2E8F0; font-size: 14px;"),
                Td(
                    Span(role.capitalize(), style=f"background: rgba(41,181,232,0.1); color: {role_badge_color}; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;"),
                    style="padding: 12px 16px;"
                ),
                Td(
                    Span(status.capitalize(), style=f"color: {status_color}; font-size: 13px;"),
                    style="padding: 12px 16px;"
                ),
            )
        )

    return Div(
        Style("""
            .org-header { margin-bottom: 32px; }
            .org-title { font-size: 24px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.4px; }
            .org-slug { font-size: 13px; color: #475569; margin-top: 4px; }
            .section-card { background: #0F1929; border: 1px solid rgba(148,163,184,0.1); border-radius: 10px; padding: 24px; margin-bottom: 24px; }
            .section-title { font-size: 15px; font-weight: 600; color: #F8FAFC; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
            .invite-btn { background: #29b5e8; color: #020617; font-size: 13px; font-weight: 600; padding: 7px 14px; border: none; border-radius: 6px; cursor: pointer; font-family: 'Inter', sans-serif; text-decoration: none; }
            .invite-btn:hover { opacity: 0.88; }
            table { width: 100%; border-collapse: collapse; }
            th { text-align: left; padding: 8px 16px; font-size: 12px; font-weight: 500; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid rgba(148,163,184,0.1); }
            tr + tr td { border-top: 1px solid rgba(148,163,184,0.06); }
        """),
        Div(
            H1(org["name"], cls="org-title"),
            P(f"app.opendata.london/org/{org['slug']}", cls="org-slug"),
            cls="org-header"
        ),
        Div(
            Div(
                Span("Members", style="font-size: 15px; font-weight: 600; color: #F8FAFC;"),
                A("+ Invite member", href=f"/org/{org['slug']}/invite", cls="invite-btn"),
                cls="section-title"
            ),
            Table(
                Thead(Tr(
                    Th("Email"),
                    Th("Role"),
                    Th("Status"),
                )),
                Tbody(*member_rows) if member_rows else Tbody(
                    Tr(Td("No members yet.", colspan="3", style="padding: 16px; color: #475569; font-size: 14px;"))
                ),
            ),
            cls="section-card"
        ),
    )
