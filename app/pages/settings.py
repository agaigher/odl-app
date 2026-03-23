from fasthtml.common import *
from app.supabase_db import db_select

def OrganizationSettings(user_id: str, session: dict):
    # Fetch active organisation context
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships:
            return Div("You are not part of any organization.", cls="error-text")
            
        org_id = memberships[0]["org_id"]
        current_user_role = memberships[0].get("role", "member")
        orgs = db_select("organisations", {"id": org_id})
        org_name = orgs[0]["name"] if orgs else "Unknown"
        org_slug = orgs[0]["slug"] if orgs else ""
        avatar_url = orgs[0].get("avatar_url") if orgs else None
        billing_email = orgs[0].get("billing_email") or ""
        
        all_members = db_select("memberships", {"org_id": org_id, "status": "active"})
        other_members = [m for m in all_members if m["user_id"] != user_id]
        
        # Fetch Audit Logs
        audit_logs = db_select("audit_logs", {"org_id": org_id}, order="created_at.desc", limit=20)
        # Create a mapping of user_id to email for better display
        user_map = {m["user_id"]: (m.get("invited_email") or m.get("user_id")) for m in all_members if m.get("user_id")}
        # Fetch SSO Config
        sso_configs = db_select("sso_configurations", {"org_id": org_id})
        sso_config = sso_configs[0] if sso_configs else {}
    except Exception as e:
        return Div(f"Error loading organization details: {e}", cls="error-text")
        
    return Div(
        Style("""
            .settings-card {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 32px;
                margin-bottom: 32px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }
            .settings-card-title {
                font-size: 18px;
                font-weight: 600;
                color: #1E293B;
                margin-bottom: 8px;
            }
            .settings-card-desc {
                font-size: 14px;
                color: #64748B;
                margin-bottom: 24px;
            }
            .danger-border {
                border-color: #FCA5A5 !important;
            }
            .danger-text { color: #DC2626 !important; }
            .danger-btn {
                background: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
            }
            .danger-btn:hover { background: #FEE2E2; }
            
            .fieldset-row { display: flex; align-items: flex-end; gap: 16px; margin-bottom: 16px; }
            .fieldset-row .input-grp { flex: 1; }
            .input-grp label { display: block; font-size: 14px; font-weight: 500; color: #334155; margin-bottom: 8px; }
            
            .divider { height: 1px; background: #E2E8F0; margin: 32px 0; }
        """),
        
        # Header
        Div(
            H2("Organization Settings", style="margin: 0; font-size: 28px; color: #0F172A;"),
            P("Manage your organization profile and extreme settings.", style="margin: 6px 0 32px 0; color: #64748B; font-size: 15px;"),
        ),
        
        # General Settings Card
        Div(
            Div("General Settings", cls="settings-card-title"),
            Div("Update your organization's identity.", cls="settings-card-desc"),
            
            # Avatar Upload
            Div(
                Img(src=avatar_url or f"https://ui-avatars.com/api/?name={org_name}&background=F1F5F9&color=0284C7", style="width: 64px; height: 64px; border-radius: 8px; object-fit: cover; border: 1px solid #E2E8F0; flex-shrink: 0;"),
                Form(
                    Input(type="file", name="avatar_file", accept="image/*", cls="odl-input", style="max-width: 250px; padding: 6px; margin: 0;"),
                    Button("Upload Logo", type="submit", cls="odl-btn-secondary", style="padding: 8px 16px;"),
                    hx_post="/settings/avatar",
                    hx_encoding="multipart/form-data",
                    style="display: flex; gap: 12px; align-items: center; margin: 0;"
                ),
                style="display: flex; gap: 20px; align-items: center; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #F1F5F9;"
            ),
            
            Form(
                Div(
                    Div(
                        Label("Organization Name"),
                        Input(type="text", name="org_name", value=org_name, cls="odl-input", style="margin-bottom: 0;"),
                        cls="input-grp"
                    ),
                    Button("Save", type="submit", cls="odl-btn-primary"),
                    cls="fieldset-row"
                ),
                hx_post="/settings/rename",
                hx_swap="innerHTML"
            ),
            
            Div(
                Div(
                    Label("Organization URL Slug", style="display:block; font-size:14px; font-weight:500; color:#334155; margin-bottom:8px;"),
                    Input(type="text", value=org_slug, cls="odl-input", disabled=True, style="background:#F8FAFC; color:#94A3B8; cursor:not-allowed; margin-bottom:0; max-width: 400px;"),
                    style="margin-top: 24px;"
                ),
                Div("The unique slash URL used to access this organization's projects. Contact support to transfer slugs.", style="font-size:12px; color:#94A3B8; margin-top:8px;")
            ),
            cls="settings-card"
        ),
        
        # Billing Configuration Card
        Div(
            Div("Billing Configuration", cls="settings-card-title"),
            Div("Configure where invoices and billing alerts are sent.", cls="settings-card-desc"),
            
            Form(
                Div(
                    Div(
                        Label("Billing Email Address"),
                        Input(type="email", name="billing_email", value=billing_email, placeholder="finance@company.com", cls="odl-input", style="margin-bottom: 0;"),
                        cls="input-grp"
                    ),
                    Button("Update", type="submit", cls="odl-btn-primary"),
                    cls="fieldset-row"
                ),
                hx_post="/settings/billing",
                hx_swap="innerHTML"
            ),
            
            Div("If empty, we'll send invoices to the primary account email.", style="font-size:12px; color:#94A3B8; margin-top:8px;"),
            cls="settings-card"
        ),
        
        # Enterprise Security Card
        Div(
            Div("Enterprise Security", cls="settings-card-title"),
            Div("Configure Single Sign-On (SSO) and domain enforcement.", cls="settings-card-desc"),
            
            Form(
                Div(
                    Div(
                        Label("Managed Domain"),
                        Input(type="text", name="domain", value=sso_config.get("domain", ""), placeholder="company.com", cls="odl-input", style="margin-bottom: 0;"),
                        cls="input-grp"
                    ),
                    Div(
                        Label("SAML Metadata URL"),
                        Input(type="url", name="metadata_url", value=sso_config.get("metadata_url", ""), placeholder="https://idp.com/saml/metadata", cls="odl-input", style="margin-bottom: 0;"),
                        cls="input-grp"
                    ),
                    style="margin-bottom: 24px;"
                ),
                
                Div(
                    Label(
                        Input(type="checkbox", name="is_active", checked=sso_config.get("is_active", False), style="margin-right: 8px;"),
                        "Enforce SSO for all organization members",
                        style="font-size: 14px; color: #334155; display: flex; align-items: center; cursor: pointer;"
                    ),
                    style="margin-bottom: 24px;"
                ),
                
                Button("Save SSO Configuration", type="submit", cls="odl-btn-primary"),
                
                hx_post="/settings/sso",
                hx_swap="innerHTML"
            ),
            
            Div("Once enabled, members will be redirected to your SAML provider to sign in.", style="font-size:12px; color:#94A3B8; margin-top:16px;"),
            cls="settings-card"
        ),
        
        # Danger Zone Card
        Div(
            Div("Danger Zone", cls="settings-card-title danger-text"),
            Div("These capabilities are destructive and cannot be completely recovered immediately.", cls="settings-card-desc"),
            
            Div(
                Div(
                    Div("Transfer Ownership", style="font-weight: 600; color: #1E293B; margin-bottom: 4px;"),
                    Div("Transfer this organization to another user.", style="font-size: 13px; color: #64748B;"),
                    style="flex: 1;"
                ),
                (Div("Only organization owners can execute transfers.", style="font-size: 13px; color: #DC2626;") if current_user_role != 'owner' else
                 Form(
                     Div(
                         Select(
                             *[Option(m.get("invited_email") or m.get("user_id", "Unknown"), value=m["user_id"]) for m in other_members],
                             name="target_user_id", cls="odl-input", style="margin-bottom: 0px; width: 280px;"
                         ) if other_members else Div("No active peers available.", style="font-size: 13px; color: #64748B; margin-right: 12px;"),
                         Button("Transfer", type="submit", cls="odl-btn-secondary", disabled=not other_members, onclick="return confirm('WARNING: You will instantly lose owner privileges. Proceed?');"),
                         style="display: flex; gap: 12px; align-items: center;"
                     ),
                     hx_post="/settings/transfer",
                     hx_target="body"
                 )),
                style="display: flex; align-items: center; justify-content: space-between; padding: 20px 0; border-top: 1px solid #E2E8F0;"
            ),
            
            Div(
                Div(
                    Div("Delete Organization", style="font-weight: 600; color: #1E293B; margin-bottom: 4px;"),
                    Div("Completely unrecoverable. This deletes all integrations, active projects, and permanently voids any prepaid API credits.", style="font-size: 13px; color: #64748B;"),
                    style="flex: 1;"
                ),
                Form(
                    Button("Delete Organization", type="submit", cls="danger-btn", onclick="return confirm('Are you absolutely certain? This will delete the entire organization, all inner projects, API keys, and flush all remaining pipeline credits immediately.');"),
                    hx_post="/settings/delete"
                ),
                style="display: flex; align-items: center; justify-content: space-between; padding: 20px 0; border-top: 1px solid #E2E8F0;"
            ),
            
            cls="settings-card danger-border"
        ),
        
        # Audit Logs Card
        Div(
            Div("Audit Logs", cls="settings-card-title"),
            Div("The last 20 administrative actions performed in this organization.", cls="settings-card-desc"),
            
            Table(
                Thead(Tr(
                    Th("Time", style="text-align: left; padding: 12px; font-size: 12px; color: #64748B;"),
                    Th("Actor", style="text-align: left; padding: 12px; font-size: 12px; color: #64748B;"),
                    Th("Action", style="text-align: left; padding: 12px; font-size: 12px; color: #64748B;"),
                    Th("Resource", style="text-align: left; padding: 12px; font-size: 12px; color: #64748B;"),
                )),
                Tbody(
                    *[Tr(
                        Td(log["created_at"][:16].replace("T", " "), style="padding: 12px; font-size: 13px; color: #475569;"),
                        Td(user_map.get(log["actor_id"], "System"), style="padding: 12px; font-size: 13px; color: #475569;"),
                        Td(log["action"], style="padding: 12px; font-size: 13px; font-weight: 500; color: #1E293B;"),
                        Td(f"{log.get('resource_type', '')}: {log.get('resource_id', '')}" if log.get('resource_type') else "—", style="padding: 12px; font-size: 12px; font-family: monospace; color: #64748B;"),
                        style="border-top: 1px solid #F1F5F9;"
                    ) for log in audit_logs]
                ) if audit_logs else Tbody(Tr(Td("No actions recorded yet.", colspan="4", style="padding: 32px; text-align: center; color: #94A3B8;"))),
                style="width: 100%; border-collapse: collapse; margin-top: 16px;"
            ),
            cls="settings-card"
        )
    )
