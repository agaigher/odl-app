from fasthtml.common import *
from app.supabase_db import db_select

def OrganizationSettings(user_id: str, session: dict):
    # Fetch active organisation context
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships:
            return Div("You are not part of any organization.", cls="error-text")
            
        org_id = memberships[0]["org_id"]
        orgs = db_select("organisations", {"id": org_id})
        org_name = orgs[0]["name"] if orgs else "Unknown"
        org_slug = orgs[0]["slug"] if orgs else ""
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
            Div("Update your organization's display name.", cls="settings-card-desc"),
            
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
                Button("Transfer", cls="odl-btn-secondary", disabled=True, style="cursor:not-allowed; opacity: 0.5;", title="Coming soon"),
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
        )
    )
