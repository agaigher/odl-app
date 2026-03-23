from fasthtml.common import *
from app.components import icon_svg, IC


def OrganisationsPage(orgs):
    return Div(
        Div(
            Div(
                H1("Organizations", style="font-size: 24px; font-weight: 700; color: #F8FAFC;"),
                P("Manage your workspaces and billing across different organizations.", style="color: #94A3B8; font-size: 14px; margin-top: 4px;"),
            ),
            A(
                icon_svg(IC.plus_circle, style="margin-right: 8px; width: 16px; height: 16px;"),
                "New Organization",
                href="/create-org",
                style="background: #0284C7; color: white; padding: 10px 18px; border-radius: 8px; font-weight: 600; text-decoration: none; display: flex; align-items: center; transition: background 0.2s;"
            , cls="new-org-btn"),
            style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px;"
        ),

        Div(
            *[OrgCard(o) for o in orgs] if orgs else EmptyState(),
            style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px;"
        ),

        Style("""
            .new-org-btn:hover { background: #0369A1 !important; }
            .org-card {
                background: #1E293B; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;
                padding: 24px; transition: all 0.2s; text-decoration: none;
                display: flex; flex-direction: column; cursor: pointer;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .org-card:hover { border-color: #0284C7; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2); transform: translateY(-2px); }
            .org-logo-large {
                width: 48px; height: 48px; border-radius: 8px;
                background: #0F172A; border: 1px solid rgba(255,255,255,0.05);
                display: flex; align-items: center; justify-content: center;
                margin-bottom: 16px; font-weight: 700; color: #94A3B8; font-size: 20px;
                object-fit: cover;
            }
            .org-name { font-size: 18px; font-weight: 700; color: #F8FAFC; margin-bottom: 8px; }
            .org-stats-row {
                display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
                margin-top: 4px;
            }
            .org-stat-pill {
                display: inline-flex; align-items: baseline; gap: 6px;
                font-size: 13px; color: #94A3B8;
            }
            .org-stat-num {
                font-family: 'JetBrains Mono', ui-monospace, monospace;
                font-size: 15px; font-weight: 600; color: #F1F5F9;
            }
            .org-card-hint {
                margin-top: 14px; font-size: 12px; color: #64748B;
            }
        """),
        cls="organisations-container"
    )


def OrgCard(org):
    n_proj = org.get("project_count", 0)
    n_mem = org.get("member_count", 0)
    return A(
        Img(src=org.get("avatar_url"), cls="org-logo-large") if org.get("avatar_url") else
        Div(org["name"][0].upper(), cls="org-logo-large"),

        Div(org["name"], cls="org-name"),
        Div(
            Div(
                Span(str(n_proj), cls="org-stat-num"),
                Span("projects"),
                cls="org-stat-pill",
            ),
            Div(
                Span(str(n_mem), cls="org-stat-num"),
                Span("members"),
                cls="org-stat-pill",
            ),
            cls="org-stats-row",
        ),
        P("Opens this org in the app → Projects", cls="org-card-hint"),

        href=f"/org/open/{org['slug']}",
        cls="org-card",
    )


def EmptyState():
    return Div(
        Div(icon_svg(IC.plus_circle), style="width: 48px; height: 48px; color: #CBD5E1; margin: 0 auto 16px;"),
        H3("No organizations found", style="font-size: 16px; font-weight: 600; color: #F8FAFC;"),
        P("You aren't part of any organizations yet. Create one to get started.", style="color: #94A3B8; font-size: 14px; margin-top: 8px;"),
        A("Create Organization", href="/create-org", style="display: inline-block; margin-top: 20px; color: white; background: #0284C7; padding: 8px 20px; border-radius: 6px; text-decoration: none;"),
        style="grid-column: 1 / -1; text-align: center; padding: 80px 20px; border: 2px dashed rgba(255,255,255,0.05); border-radius: 12px; background: #1E293B;"
    )
