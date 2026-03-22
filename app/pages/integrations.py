from fasthtml.common import *
from app.supabase_db import db_select

INTEGRATIONS_STYLE = Style("""
    .int-wrap { max-width: 800px; margin: 0 auto; padding: 20px 0; }
    .int-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .int-title { font-size: 24px; font-weight: 700; color: #1E293B; letter-spacing: -0.3px; }
    .int-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }
    .int-info h3 { font-size: 16px; font-weight: 600; color: #1E293B; margin-bottom: 4px; }
    .int-info p { font-size: 13px; color: #64748B; }
    .int-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; margin-right: 10px; text-transform: uppercase; letter-spacing: 0.05em; }
    .badge-api { background: #E0F2FE; color: #0284C7; }
    .badge-sf { background: #EFF6FF; color: #3B82F6; }
    .int-actions button { background: #FFFFFF; color: #EF4444; border: 1px solid #FECACA; padding: 6px 12px; border-radius: 5px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
    .int-actions button:hover { background: #FEE2E2; border-color: #F87171; }
    
    .add-int-form { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-top: 30px; display: flex; gap: 12px; align-items: center; }
    .add-int-input { flex: 1; padding: 10px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 14px; outline: none; font-family: 'Inter', sans-serif; }
    .add-int-input:focus { border-color: #0284C7; box-shadow: 0 0 0 3px rgba(2,132,199,0.1); }
    .add-int-select { padding: 10px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 14px; background: #FFFFFF; cursor: pointer; outline: none; font-family: 'Inter', sans-serif; }
    .add-int-btn { background: #0284C7; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s; font-family: 'Inter', sans-serif; white-space: nowrap; }
    .add-int-btn:hover { background: #0369A1; }
    .empty-ints { text-align: center; padding: 40px; color: #64748B; font-size: 14px; border: 1px dashed #CBD5E1; border-radius: 10px; background: #FAFAFA; }
""")

def _integration_row(row):
    badge_cls = "badge-api" if row.get("type") == "api" else "badge-sf"
    type_label = "API Key" if row.get("type") == "api" else "Snowflake"
    created = row.get("created_at", "")[:10] if row.get("created_at") else "Just now"
    return Div(
        A(
            Span(type_label, cls=f"int-badge {badge_cls}"),
            H3(row.get("name", "Unnamed"), style="display: inline-block; vertical-align: middle; margin: 0; color: #1E293B;"),
            P(f"Created on {created}", style="margin-top: 6px;"),
            href=f"/integrations/{row['id']}",
            cls="int-info",
            style="text-decoration: none; flex: 1; display: block;"
        ),
        Div(
            Button("Delete", hx_post=f"/integrations/{row['id']}/delete", hx_target=f"#int-{row['id']}", hx_swap="outerHTML"),
            cls="int-actions"
        ),
        cls="int-card",
        id=f"int-{row['id']}"
    )

def IntegrationsView(user_id: str):
    try:
        ints = db_select("user_integrations", {"user_id": user_id})
        ints.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    except Exception:
        ints = []
    
    list_content = Div(*[_integration_row(r) for r in ints], id="integrations-list") if ints else Div("No integrations created yet. Add your first connection below!", cls="empty-ints", id="integrations-list")

    add_form = Form(
        Input(type="text", name="name", placeholder="e.g. Production Data App", cls="add-int-input", required=True),
        Select(
            Option("API Key", value="api"),
            Option("Snowflake Account", value="snowflake"),
            name="type", cls="add-int-select"
        ),
        Button("Create", type="submit", cls="add-int-btn"),
        hx_post="/integrations/create",
        hx_target="#integrations-list",
        hx_swap="beforeend" if ints else "outerHTML",
        cls="add-int-form"
    )

    return Div(
        INTEGRATIONS_STYLE,
        Div(
            H1("Data Integrations", cls="int-title"),
            cls="int-header"
        ),
        P("Manage your API keys and Snowflake connection targets here. You can cleanly assign datasets to these integrations directly from the catalog.", style="color: #64748B; margin-bottom: 24px; font-size: 14px; line-height: 1.6;"),
        list_content,
        add_form,
        cls="int-wrap"
    )
