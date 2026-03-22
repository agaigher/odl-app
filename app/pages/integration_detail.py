from fasthtml.common import *
from app.supabase_db import db_select
import random

DETAIL_STYLE = Style("""
    .int-detail-wrap { max-width: 900px; margin: 0 auto; padding: 20px 0; }
    .int-header { margin-bottom: 30px; }
    .int-back { display: inline-flex; align-items: center; gap: 5px; color: #64748B; font-size: 13px; text-decoration: none; font-weight: 500; margin-bottom: 20px; transition: color 0.15s; }
    .int-back:hover { color: #0F1929; }
    .int-title { font-size: 28px; font-weight: 700; color: #1E293B; letter-spacing: -0.4px; display: flex; align-items: center; gap: 10px; }
    .int-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
    .badge-api { background: #E0F2FE; color: #0284C7; }
    .badge-sf { background: #EFF6FF; color: #3B82F6; }
    
    .stats-row { display: flex; gap: 16px; margin-bottom: 30px; }
    .stat-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; flex: 1; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .stat-val { font-size: 24px; font-weight: 700; color: #1E293B; font-family: 'Roboto Mono', monospace; margin-bottom: 4px; }
    .stat-label { font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }

    .section-title { font-size: 16px; font-weight: 600; color: #1E293B; margin-bottom: 14px; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; }
    .content-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 24px; margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    
    .ds-list { display: flex; flex-direction: column; gap: 10px; }
    .ds-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; border: 1px solid #F1F5F9; border-radius: 8px; background: #FAFAFA; transition: background 0.15s; }
    .ds-item:hover { background: #F8FAFC; border-color: #E2E8F0; }
    .ds-item-name { font-size: 14px; font-weight: 600; color: #334155; text-decoration: none; }
    .ds-item-name:hover { color: #0284C7; }
    .ds-remove { background: #FFFFFF; border: 1px solid #E2E8F0; color: #EF4444; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
    .ds-remove:hover { border-color: #F87171; background: #FEF2F2; }
    
    .guide-block { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; font-family: 'Roboto Mono', monospace; font-size: 13px; color: #0F1929; overflow-x: auto; white-space: pre-wrap; line-height: 1.5; margin-bottom: 14px; }
    
    .org-list { display: flex; flex-direction: column; gap: 8px; }
    .org-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border: 1px solid #E2E8F0; border-radius: 8px; background: #FFFFFF; }
    .org-user { font-size: 14px; font-weight: 500; color: #1E293B; display: flex; align-items: center; gap: 10px;}
    .org-role { font-size: 11px; color: #64748B; background: #F1F5F9; padding: 2px 8px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
    .toggle-btn { background: #E2E8F0; color: #64748B; border: none; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s; min-width: 80px; text-align: center; }
    .toggle-btn.on { background: #0284C7; color: #FFFFFF; }
    .empty-state { text-align: center; padding: 30px; color: #64748B; font-size: 14px; font-style: italic; }
""")

def IntegrationDetailView(integration_id: str, user_id: str):
    try:
        ints = db_select("user_integrations", {"id": integration_id, "user_id": user_id})
        if not ints: return Div("Integration not found.", cls="empty-state")
        integration = ints[0]
    except Exception:
        return Div("Integration not found.", cls="empty-state")

    itype = integration.get("type", "api")
    name = integration.get("name", "Unnamed")
    
    # Fetch Datasets
    try:
        linked = db_select("dataset_integrations", {"integration_id": integration_id})
    except Exception:
        linked = []
    
    for ds in linked:
        try:
            full = db_select("datasets", {"slug": ds["dataset_slug"]})
            if full: ds["title"] = full[0].get("title")
        except: pass

    # Fetch Mock Usage
    usage_count = random.randint(10, 450) if linked else 0
    
    # Guide HTML
    if itype == "api":
        guide_html = Div(
            H3("Using your API Key", style="font-size:14px; color:#1E293B; margin-bottom:10px;"),
            P("Pass this integration key as a Bearer token in the Authorization header to query attached datasets.", style="font-size:13px; color:#64748B; margin-bottom:12px;"),
            Div(f'curl -X GET "https://api.opendata.london/v1/datasets/..." \\\n  -H "Authorization: Bearer YOUR_API_KEY"', cls="guide-block")
        )
    else:
        guide_html = Div(
            H3("Using Snowflake Zero-copy Shares", style="font-size:14px; color:#1E293B; margin-bottom:10px;"),
            P("Datasets attached to this integration target are instantly available in your Snowflake warehouse.", style="font-size:13px; color:#64748B; margin-bottom:12px;"),
            Div(f"SELECT * \nFROM LONDON_DB.PUBLIC.<DATASET_SLUG>\nLIMIT 100;", cls="guide-block")
        )

    # Datasets
    if not linked:
        ds_list = Div("No datasets attached yet. Add datasets from the Catalog.", cls="empty-state")
    else:
        ds_list = Div(*[
            Div(
                A(ds.get("title") or ds["dataset_slug"], href=f"/catalog/{ds['dataset_slug']}", cls="ds-item-name"),
                Button("Remove", hx_post=f"/integrations/{integration_id}/remove-dataset/{ds['dataset_slug']}", hx_target=f"#ds-{ds['dataset_slug']}", hx_swap="outerHTML", cls="ds-remove"),
                cls="ds-item", id=f"ds-{ds['dataset_slug']}"
            ) for ds in linked
        ], cls="ds-list")

    # Org Access Control
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        org_id = memberships[0]["org_id"] if memberships else None
    except:
        org_id = None

    if org_id:
        try:
            all_members = db_select("memberships", {"org_id": org_id, "status": "active"})
            shared_with = db_select("integration_members", {"integration_id": integration_id})
            shared_ids = {m["user_id"] for m in shared_with}
            
            org_rows = []
            for m in all_members:
                mid = m["user_id"]
                if mid == user_id: continue # skip owner
                
                m_email = m.get("invited_email", "Member")
                if not m_email or m_email == "Member":
                    try:
                        # Grab email from user auth table if possible (fallback method mocked)
                        m_email = "Member " + str(mid)[:5]
                    except: pass

                has_access = mid in shared_ids
                
                btn = Button("Revoke" if has_access else "Grant",
                             hx_post=f"/integrations/{integration_id}/toggle-access/{mid}",
                             hx_target="this", hx_swap="outerHTML",
                             cls=f"toggle-btn {'on' if has_access else ''}")
                org_rows.append(
                    Div(
                        Div(m_email, Span(m.get("role", "member"), cls="org-role"), cls="org-user"),
                        btn,
                        cls="org-item"
                    )
                )
            org_content = Div(*org_rows, cls="org-list") if org_rows else P("You are the only member of this organisation.", cls="empty-state")
        except:
            org_content = P("Failed to load organisation members.", cls="empty-state")
    else:
        org_content = P("You are not part of an organisation. Create one to share integrations.", style="color: #64748B; font-size: 13px; padding: 20px; text-align: center;")


    return Div(
        DETAIL_STYLE,
        A("← Back to Integrations", href="/integrations", cls="int-back"),
        Div(
            H1(
                name, 
                Span("API Key" if itype == "api" else "Snowflake", cls=f"int-badge badge-{itype}"),
                cls="int-title"
            ),
            cls="int-header"
        ),
        
        Div(
            Div(P("Linked Datasets", cls="stat-label"), P(str(len(linked)), cls="stat-val"), cls="stat-card"),
            Div(P("Times Used", cls="stat-label"), P(str(usage_count), cls="stat-val"), cls="stat-card"),
            cls="stats-row"
        ),
        
        Div(
            H2("Connection Guide", cls="section-title"),
            guide_html,
            cls="content-card"
        ),
        
        Div(
            H2("Attached Datasets", cls="section-title"),
            ds_list,
            cls="content-card"
        ),
        
        Div(
            H2("Organisation Access", cls="section-title"),
            P("Select which members of your organisation can use this integration target.", style="font-size: 13px; color: #64748B; margin-bottom: 16px;"),
            org_content,
            cls="content-card"
        ),
        
        cls="int-detail-wrap"
    )
