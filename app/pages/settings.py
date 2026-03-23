from fasthtml.common import *
from app.supabase_db import db_select
from app.components import icon_svg, IC

def OrganizationSettings(user_id: str, session: dict, tab: str = 'general'):
    # Fetch active organisation context
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships:
            return Div("You are not part of any organization.", cls="error-text")
            
        org_id = memberships[0]["org_id"]
        role = memberships[0].get("role", "member")
        orgs = db_select("organisations", {"id": org_id})
        if not orgs: return Div("Organization not found.", cls="error-text")
        org = orgs[0]
        
    except Exception as e:
        return Div(f"Error loading organization details: {e}", cls="error-text")

    # The Pane Content
    pane = (
        GeneralPane(org) if tab == 'general' else
        SecurityPane(org, user_id, role) if tab == 'security' else
        SSOPane(org) if tab == 'sso' else
        AuditPane(org) if tab == 'audit' else
        PlaceholderPane(tab.replace('-', ' ').title()) if tab in ('oauth', 'legal') else
        GeneralPane(org)
    )

    # If this is an HTMX request for the pane only, we return just the pane
    # This is handled in main.py by checking headers, but we can also handle it here 
    # if we want to return just the Pane wrapped in the content Div.

    # Layout for Settings
    return Div(
        Style("""
            .settings-container {
                display: flex;
                gap: 48px;
                padding: 40px;
                max-width: 1200px;
                margin: 0 auto;
            }
            .settings-nav {
                width: 200px;
                flex-shrink: 0;
            }
            .settings-content {
                flex: 1;
                max-width: 800px;
            }
            .nav-group {
                margin-bottom: 32px;
            }
            .nav-group-title {
                font-size: 11px;
                font-weight: 700;
                color: #94A3B8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 12px;
                padding-left: 12px;
            }
            .nav-tab {
                display: block;
                padding: 8px 12px;
                font-size: 14px;
                color: #64748B;
                text-decoration: none;
                border-radius: 6px;
                transition: all 0.2s;
                margin-bottom: 2px;
                cursor: pointer;
            }
            .nav-tab:hover {
                background: #F8FAFC;
                color: #0F172A;
            }
            .nav-tab.active {
                background: #F1F5F9;
                color: #0F172A;
                font-weight: 600;
            }
            
            /* Shared Card Styles */
            .settings-card {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 32px;
                margin-bottom: 32px;
            }
            .card-title { font-size: 18px; font-weight: 600; color: #1E293B; margin-bottom: 8px; }
            .card-desc { font-size: 14px; color: #64748B; margin-bottom: 24px; }
            .danger-border { border-color: #FCA5A5 !important; }
            .danger-text { color: #DC2626 !important; }
            
            .fieldset-row { display: flex; align-items: flex-end; gap: 16px; margin-bottom: 16px; }
            .fieldset-row .input-grp { flex: 1; }
            .input-grp label { display: block; font-size: 14px; font-weight: 500; color: #334155; margin-bottom: 8px; }
        """),
        
        Div(
            # Secondary Sidebar
            Div(
                Div(
                    Div("Configuration", cls="nav-group-title"),
                    A("General", hx_get="/settings?tab=general", hx_target="#settings-layout", hx_push_url="true", cls=f"nav-tab {'active' if tab == 'general' else ''}"),
                    A("Security", hx_get="/settings?tab=security", hx_target="#settings-layout", hx_push_url="true", cls=f"nav-tab {'active' if tab == 'security' else ''}"),
                    A("SSO", hx_get="/settings?tab=sso", hx_target="#settings-layout", hx_push_url="true", cls=f"nav-tab {'active' if tab == 'sso' else ''}"),
                    cls="nav-group"
                ),
                Div(
                    Div("Connections", cls="nav-group-title"),
                    A("OAuth Apps", hx_get="/settings?tab=oauth", hx_target="#settings-layout", hx_push_url="true", cls=f"nav-tab {'active' if tab == 'oauth' else ''}"),
                    cls="nav-group"
                ),
                Div(
                    Div("Compliance", cls="nav-group-title"),
                    A("Audit Logs", hx_get="/settings?tab=audit", hx_target="#settings-layout", hx_push_url="true", cls=f"nav-tab {'active' if tab == 'audit' else ''}"),
                    A("Legal Documents", hx_get="/settings?tab=legal", hx_target="#settings-layout", hx_push_url="true", cls=f"nav-tab {'active' if tab == 'legal' else ''}"),
                    cls="nav-group"
                ),
                cls="settings-nav",
                id="settings-secondary-nav"
            ),
            
            # Content Pane
            Div(
                pane,
                cls="settings-content",
                id="settings-content-wrap"
            ),
            cls="settings-container",
            id="settings-layout"
        )
    )

def GeneralPane(org):
    return Div(
        H2("General Settings", style="font-size: 24px; font-weight: 700; margin-bottom: 8px;"),
        P("Manage your organization's public profile and identity.", style="color: #64748B; margin-bottom: 32px;"),
        
        # Logo Card
        Div(
            Div("Organization Logo", cls="card-title"),
            Div("This logo will be visible to all members of the organization.", cls="card-desc"),
            Div(
                Img(src=org.get("avatar_url") or f"https://ui-avatars.com/api/?name={org['name']}&background=F1F5F9&color=0284C7", style="width: 64px; height: 64px; border-radius: 8px; border: 1px solid #E2E8F0;"),
                Form(
                    Input(type="file", name="avatar_file", accept="image/*", cls="odl-input", style="max-width: 250px; padding: 6px;"),
                    Button("Upload", type="submit", cls="odl-btn-secondary"),
                    hx_post="/settings/avatar", hx_encoding="multipart/form-data",
                    style="display: flex; gap: 12px; align-items: center;"
                ),
                style="display: flex; gap: 24px; align-items: center;"
            ),
            cls="settings-card"
        ),
        
        # Name Card
        Div(
            Div("Display Name", cls="card-title"),
            Div("The name shown throughout the application.", cls="card-desc"),
            Form(
                Div(
                    Input(type="text", name="org_name", value=org["name"], cls="odl-input", style="flex: 1; margin: 0;"),
                    Button("Save", type="submit", cls="odl-btn-primary"),
                    style="display: flex; gap: 12px;"
                ),
                hx_post="/settings/rename"
            ),
            cls="settings-card"
        ),
        id="general-pane"
    )

def SecurityPane(org, user_id, current_role):
    all_members = db_select("memberships", {"org_id": org["id"], "status": "active"})
    other_members = [m for m in all_members if m["user_id"] != user_id]
    
    return Div(
        H2("Security & Access", style="font-size: 24px; font-weight: 700; margin-bottom: 8px;"),
        P("Manage organization ownership and protection.", style="color: #64748B; margin-bottom: 32px;"),
        
        # Transfer Ownership
        Div(
            Div("Transfer Ownership", cls="card-title"),
            Div("Hand over the organization to another team member.", cls="card-desc"),
            (P("Only organization owners can execute transfers.", style="font-size: 13px; color: #DC2626;") if current_role != 'owner' else
             Form(
                 Div(
                     Select(
                         *[Option(m.get("invited_email") or m.get("user_id", "Unknown"), value=m["user_id"]) for m in other_members],
                         name="target_user_id", cls="odl-input", style="flex: 1; margin: 0;"
                     ) if other_members else Div("No team members found.", style="color: #64748B;"),
                     Button("Transfer", type="submit", cls="odl-btn-secondary", disabled=not other_members, onclick="return confirm('WARNING: You will lose owner status. Proceed?');"),
                     style="display: flex; gap: 12px;"
                 ),
                 hx_post="/settings/transfer", hx_target="body"
             )),
            cls="settings-card"
        ),
        
        # Delete Org
        Div(
            Div("Delete Organization", cls="card-title danger-text"),
            Div("Permanently delete this organization and all its data.", cls="card-desc"),
            Form(
                Button("Delete Organization", type="submit", style="background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer;",
                       onclick="return confirm('Are you absolutely sure? This cannot be undone.');"),
                hx_post="/settings/delete"
            ),
            cls="settings-card danger-border"
        ),
        id="security-pane"
    )

def SSOPane(org):
    sso_configs = db_select("sso_configurations", {"org_id": org["id"]})
    sso = sso_configs[0] if sso_configs else {}
    
    return Div(
        H2("Single Sign-On (SSO)", style="font-size: 24px; font-weight: 700; margin-bottom: 8px;"),
        P("Configure domain-wide authentication enforcement.", style="color: #64748B; margin-bottom: 32px;"),
        
        Div(
            Div("SAML Configuration", cls="card-title"),
            Div("Connect your enterprise identity provider.", cls="card-desc"),
            Form(
                Div(
                    Label("Managed Domain", style="font-size: 13px; font-weight: 600; color: #334155; display: block; margin-bottom: 6px;"),
                    Input(type="text", name="domain", value=sso.get("domain", ""), placeholder="company.com", cls="odl-input"),
                    style="margin-bottom: 20px;"
                ),
                Div(
                    Label("Metadata URL", style="font-size: 13px; font-weight: 600; color: #334155; display: block; margin-bottom: 6px;"),
                    Input(type="url", name="metadata_url", value=sso.get("metadata_url", ""), placeholder="https://idp.com/metadata", cls="odl-input"),
                    style="margin-bottom: 20px;"
                ),
                Div(
                    Label(
                        Input(type="checkbox", name="is_active", checked=sso.get("is_active", False), style="margin-right: 8px;"),
                        "Enforce SSO for all members",
                        style="font-size: 14px; display: flex; align-items: center; cursor: pointer;"
                    ),
                    style="margin-bottom: 24px;"
                ),
                Button("Save Configuration", type="submit", cls="odl-btn-primary"),
                hx_post="/settings/sso"
            ),
            cls="settings-card"
        ),
        id="sso-pane"
    )

def AuditPane(org):
    all_members = db_select("memberships", {"org_id": org["id"], "status": "active"})
    user_map = {m["user_id"]: (m.get("invited_email") or m.get("user_id")) for m in all_members if m.get("user_id")}
    logs = db_select("audit_logs", {"org_id": org["id"]}, order="created_at.desc", limit=50)
    
    return Div(
        H2("Audit Logs", style="font-size: 24px; font-weight: 700; margin-bottom: 8px;"),
        P("Review recent administrative activity.", style="color: #64748B; margin-bottom: 32px;"),
        
        Div(
            Table(
                Thead(Tr(
                    Th("Time", style="text-align: left; padding: 12px; font-size: 12px; color: #64748B;"),
                    Th("Actor", style="text-align: left; padding: 12px; font-size: 12px; color: #64748B;"),
                    Th("Action", style="text-align: left; padding: 12px; font-size: 12px; color: #64748B;"),
                )),
                Tbody(
                    *[Tr(
                        Td(log["created_at"][:16].replace("T", " "), style="padding: 12px; font-size: 13px; color: #475569;"),
                        Td(user_map.get(log["actor_id"], "System"), style="padding: 12px; font-size: 13px; color: #475569;"),
                        Td(log["action"], style="padding: 12px; font-size: 13px; font-weight: 600; color: #1E293B;"),
                        style="border-top: 1px solid #F1F5F9;"
                    ) for log in logs]
                ) if logs else Tbody(Tr(Td("No logs yet.", colspan="3", style="padding: 32px; text-align: center; color: #94A3B8;"))),
                style="width: 100%; border-collapse: collapse;"
            ),
            style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden;"
        ),
        id="audit-pane"
    )

def PlaceholderPane(title):
    return Div(
        H2(f"{title} (Coming Soon)", style="font-size: 24px; font-weight: 700; margin-bottom: 8px;"),
        P(f"Configure {title} for your enterprise organization.", style="color: #64748B; margin-bottom: 32px;"),
        Div(
            Div(icon_svg(IC.bolt), style="width: 48px; height: 48px; color: #CBD5E1; margin: 0 auto 16px;"),
            P("This feature is currently under final review and will be available shortly.", style="color: #94A3B8; font-size: 14px;"),
            style="text-align: center; padding: 80px 20px; border: 2px dashed #E2E8F0; border-radius: 12px; background: #F8FAFC;"
        ),
        id=f"{title.lower().replace(' ', '-')}-pane"
    )
