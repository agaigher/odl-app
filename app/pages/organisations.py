from fasthtml.common import *
from app.components import icon_svg, IC

def OrganisationsPage(orgs):
    return Div(
        # Header
        Div(
            Div(
                H1("Organizations", style="font-size: 24px; font-weight: 700; color: #0F172A;"),
                P("Manage your workspaces and billing across different organizations.", style="color: #64748B; font-size: 14px; margin-top: 4px;"),
            ),
            A(
                icon_svg(IC.plus_circle, style="margin-right: 8px; width: 16px; height: 16px;"),
                "New Organization",
                href="/create-org",
                style="background: #0284C7; color: white; padding: 10px 18px; border-radius: 8px; font-weight: 600; text-decoration: none; display: flex; align-items: center; transition: background 0.2s;"
            , cls="new-org-btn"),
            style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px;"
        ),
        
        # Grid
        Div(
            *[OrgCard(o) for o in orgs] if orgs else EmptyState(),
            style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px;"
        ),
        
        Style("""
            .new-org-btn:hover { background: #0369A1 !important; }
            .org-card {
                background: white; border: 1px solid #E2E8F0; border-radius: 12px;
                padding: 24px; transition: all 0.2s; text-decoration: none;
                display: flex; flex-direction: column; cursor: pointer;
            }
            .org-card:hover { border-color: #0284C7; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); transform: translateY(-2px); }
            .org-logo-large {
                width: 48px; height: 48px; border-radius: 8px;
                background: #F8FAFC; border: 1px solid #E2E8F0;
                display: flex; align-items: center; justify-content: center;
                margin-bottom: 16px; font-weight: 700; color: #64748B; font-size: 20px;
                object-fit: cover;
            }
            .org-name { font-size: 18px; font-weight: 700; color: #1E293B; margin-bottom: 4px; }
            .org-meta { font-size: 13px; color: #94A3B8; display: flex; align-items: center; gap: 8px; }
            .tier-badge {
                font-size: 10px; font-weight: 700; background: #F1F5F9;
                color: #64748B; padding: 2px 6px; border-radius: 4px;
                text-transform: uppercase;
            }
            .org-action-bar {
                margin-top: 24px; padding-top: 16px; border-top: 1px solid #F1F5F9;
                display: flex; justify-content: flex-end;
            }
            .view-dashboard-btn { font-size: 13px; font-weight: 600; color: #0284C7; display: flex; align-items: center; gap: 4px; }
        """),
        cls="organisations-container"
    )

def OrgCard(org):
    return A(
        # Identity
        Img(src=org.get("avatar_url"), cls="org-logo-large") if org.get("avatar_url") else 
        Div(org["name"][0].upper(), cls="org-logo-large"),
        
        Div(org["name"], cls="org-name"),
        Div(
            Span("FREE", cls="tier-badge"),
            Span("•"),
            Span("Active", style="color: #10B981;"),
            cls="org-meta"
        ),
        
        Div(
            Span("View Dashboard", cls="view-dashboard-btn"),
            cls="org-action-bar"
        ),
        
        href=f"/org/{org['slug']}",
        # We also need a way to trigger session switch when clicking the card.
        # For simplicity, we can make the link a form or use HTMX hx-post.
        # But if they click the card, they probably want to switch anyway.
        # I'll use a script to auto-switch if they come from this page, or handle it in the /org/{slug} route.
        cls="org-card"
    )

def EmptyState():
    return Div(
        Div(icon_svg(IC.plus_circle), style="width: 48px; height: 48px; color: #CBD5E1; margin: 0 auto 16px;"),
        H3("No organizations found", style="font-size: 16px; font-weight: 600; color: #475569;"),
        P("You aren't part of any organizations yet. Create one to get started.", style="color: #94A3B8; font-size: 14px; margin-top: 8px;"),
        A("Create Organization", href="/create-org", style="display: inline-block; margin-top: 20px; color: white; background: #0284C7; padding: 8px 20px; border-radius: 6px; text-decoration: none;"),
        style="grid-column: 1 / -1; text-align: center; padding: 80px 20px; border: 2px dashed #E2E8F0; border-radius: 12px; background: #F8FAFC;"
    )
