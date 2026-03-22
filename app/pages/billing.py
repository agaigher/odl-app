from fasthtml.common import *
from app.supabase_db import db_select
from app.pages.catalog import CATALOG_STYLE

def BillingDashboard(user_id="", session=None):
    # Get active organization by querying memberships
    try:
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        org_id = memberships[0]["org_id"] if memberships else None
    except Exception:
        org_id = None
        
    if not org_id:
        return Div(
            CATALOG_STYLE,
            Div(H1("Billing", cls="fav-page-title"), cls="fav-header"),
            Div("You must be part of an Organisation to view billing details.", cls="error-text", style="padding:24px;")
        )
        
    # Get org details, including credit_balance
    try:
        orgs = db_select("organisations", {"id": org_id})
        credit_balance = orgs[0].get("credit_balance", 0) if orgs else 0
        org_name = orgs[0].get("name", "Your Organisation") if orgs else "Your Organisation"
    except Exception:
        credit_balance = 0
        org_name = "Your Organisation"

    return Div(
        CATALOG_STYLE,
        Div(H1("Billing & Usage", cls="fav-page-title"), cls="fav-header"),
        
        Div(
            # Balance Card
            Div(
                H2(org_name, style="font-size: 16px; font-weight: 600; margin-bottom: 8px; color: #0F172A;"),
                P("Current Data Credit Balance", style="font-size: 13px; color: #64748B; margin-bottom: 12px;"),
                Div(f"{credit_balance:,}", style="font-size: 36px; font-weight: 700; color: #0F172A; letter-spacing: -1px;"),
                P("Credits are drawn down seamlessly whenever your API keys query the Snowflake Data Gateway.", style="font-size: 12px; color: #94A3B8; margin-top: 12px;"),
                style="padding: 24px; background: white; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 24px;"
            ),
            
            # Purchase Card
            Div(
                H2("Purchase Credits", style="font-size: 16px; font-weight: 600; margin-bottom: 8px; color: #0F172A;"),
                P("Top up your balance to maintain uninterrupted API and Data Share access.", style="font-size: 13px; color: #64748B; margin-bottom: 24px;"),
                
                Div(
                    H3("Data Credits Package", style="font-size: 14px; font-weight: 600; margin-bottom: 4px; color: #0F172A;"),
                    P("10,000 API/Compute Queries", style="font-size: 13px; color: #475569;"),
                    Div("£10", style="font-weight: 600; font-size: 20px; color: #0284C7; margin-top: 8px; letter-spacing: -0.5px;"),
                    
                    Form(
                        Input(type="hidden", name="package", value="10k"),
                        Button("Purchase via Stripe →", type="submit", style="margin-top: 20px; background: #0F172A; color: white; padding: 12px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; border: none; cursor: pointer; width: 100%; transition: background 0.15s;"),
                        action="/billing/checkout", method="post"
                    ),
                    style="padding: 24px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0; max-width: 320px;"
                ),
                style="padding: 24px; background: white; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"
            ),
            style="display: flex; flex-direction: column; gap: 24px; max-width: 800px; margin: 0 auto; width: 100%; padding: 0 20px;"
        )
    )
