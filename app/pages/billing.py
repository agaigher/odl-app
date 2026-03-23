from fasthtml.common import *
from app.supabase_db import db_select
from app.pages.catalog import CATALOG_STYLE

def BillingDashboard(user_id="", session=None):
    # Get active organization by querying memberships
    try:
        from app.supabase_db import db_select, supabase
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
        
    # Get org details and billing ledger
    try:
        orgs = db_select("organisations", {"id": org_id})
        org = orgs[0] if orgs else {}
        ledger = db_select("billing_ledger", {"org_id": org_id}, order="created_at.desc", limit=5)
    except Exception:
        org = {}
        ledger = []

    BILLING_STYLE = Style("""
        .billing-container { max-width: 900px; margin: 0 auto; padding: 0 20px 60px; }
        .billing-section { margin-bottom: 40px; }
        .billing-section-title { font-size: 18px; font-weight: 600; color: #0F172A; margin-bottom: 4px; }
        .billing-section-desc { font-size: 14px; color: #64748B; margin-bottom: 20px; }
        
        .billing-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .billing-card-body { padding: 24px; }
        .billing-card-footer { padding: 12px 24px; background: #F8FAFC; border-top: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center; }
        
        .plan-badge { background: #F1F5F9; color: #475569; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 999px; }
        .usage-bar-wrap { margin: 20px 0; }
        .usage-bar-label { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; }
        .usage-bar { height: 8px; background: #F1F5F9; border-radius: 4px; overflow: hidden; }
        .usage-bar-fill { height: 100%; background: #0284C7; transition: width 0.3s; }
        
        .toggle-wrap { display: flex; align-items: center; justify-content: space-between; padding: 16px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0; }
        
        .invoice-table { width: 100%; border-collapse: collapse; }
        .invoice-table th { text-align: left; font-size: 12px; font-weight: 600; color: #64748B; padding: 12px 16px; border-bottom: 1px solid #E2E8F0; text-transform: uppercase; }
        .invoice-table td { padding: 14px 16px; font-size: 13px; color: #1E293B; border-bottom: 1px solid #F1F5F9; }
        .status-pill { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; text-transform: uppercase; }
        .status-paid { background: #DCFCE7; color: #15803D; }
        
        .credit-display { display: flex; align-items: baseline; gap: 8px; margin-top: 8px; }
        .credit-symbol { font-size: 20px; color: #94A3B8; font-weight: 500; }
        .credit-value { font-size: 32px; font-weight: 700; color: #0F172A; }
    """)

    return Div(
        CATALOG_STYLE,
        BILLING_STYLE,
        
        Div(
            Div(H1("Billing", cls="fav-page-title"), cls="fav-header"),
            
            # 1. Subscription Plan
            Div(
                Div("Subscription Plan", cls="billing-section-title"),
                Div("Each organization has its own subscription plan, billing cycle, and usage quotas.", cls="billing-section-desc"),
                Div(
                    Div(
                        Div(
                            Div(Span("Free Plan", cls="plan-badge"), style="margin-bottom: 16px;"),
                            H3("Included Usage", style="font-size: 15px; font-weight: 600; margin-bottom: 8px;"),
                            P("This organization is limited by the included free tier usage.", style="font-size: 13px; color: #64748B;"),
                            Div(
                                Div(
                                    Div(Span("API Queries"), Span("0 / 10,000"), cls="usage-bar-label"),
                                    Div(Div(style="width: 2%;", cls="usage-bar-fill"), cls="usage-bar"),
                                    cls="usage-bar-wrap"
                                )
                            ),
                            cls="billing-card-body"
                        ),
                        Div(
                            P("To scale seamlessly and add more seats, upgrade to a paid plan.", style="font-size: 13px; color: #64748B;"),
                            Button("Change subscription plan", cls="fav-create-btn"),
                            cls="billing-card-footer"
                        ),
                        cls="billing-card"
                    ),
                ),
                cls="billing-section"
            ),
            
            # 2. Cost Control
            Div(
                Div("Cost Control", cls="billing-section-title"),
                Div("Allow scaling beyond your plan's included quota.", cls="billing-section-desc"),
                Div(
                    Div(
                        Div(
                            H3("Spend Cap", style="font-size: 15px; font-weight: 600; margin-bottom: 4px;"),
                            P("Spend cap is currently " + ("enabled" if org.get("spend_cap_enabled", True) else "disabled"), style="font-size: 13px; color: #64748B; margin-bottom: 16px;"),
                            Div(
                                Div(
                                    Div(
                                        Span("Spend cap is enabled", style="font-size: 14px; font-weight: 500;"),
                                        P("You won't be charged extra for usage. Projects may enter read-only mode if exceeded.", style="font-size: 12px; color: #94A3B8; margin-top: 2px;"),
                                        style="flex: 1;"
                                    ),
                                    Form(
                                        Input(type="checkbox", name="enabled", checked=org.get("spend_cap_enabled", True), 
                                              style="width: 44px; height: 24px; cursor: pointer;"),
                                        hx_post="/billing/spend-cap", hx_trigger="change"
                                    ),
                                    cls="toggle-wrap"
                                )
                            ),
                            cls="billing-card-body"
                        ),
                        cls="billing-card"
                    ),
                ),
                cls="billing-section"
            ),
            
            # 3. Past Invoices
            Div(
                Div("Past Invoices", cls="billing-section-title"),
                Div("You get an invoice every time you change your plan or when your cycle resets.", cls="billing-section-desc"),
                Div(
                    Div(
                        Table(
                            Thead(Tr(
                                Th("Date"), Th("Amount"), Th("Invoice ID"), Th("Status"), Th("")
                            )),
                            Tbody(
                                *[Tr(
                                    Td(log["created_at"][:10]),
                                    Td(f"£{log['amount_paid']:,.2f}"),
                                    Td(log["stripe_session_id"][:12] + "...", style="font-family: monospace; color: #64748B;"),
                                    Td(Span(log["status"], cls="status-pill status-paid")),
                                    Td(A("View", href="#", style="color: #0284C7; font-weight: 600; text-decoration: none;")),
                                ) for log in ledger]
                            ) if ledger else Tbody(Tr(Td("No invoices found.", colspan="5", style="text-align:center; padding: 40px; color: #94A3B8;"))),
                            cls="invoice-table"
                        ),
                        cls="billing-card"
                    ),
                ),
                cls="billing-section"
            ),
            
            # 4. Payment Methods
            Div(
                Div("Payment Methods", cls="billing-section-title"),
                Div("Payments for your subscription are made using the default card.", cls="billing-section-desc"),
                Div(
                    Div(
                        Div(
                            Div(
                                Div(style="width: 40px; height: 24px; background: #F1F5F9; border-radius: 4px; margin-right: 12px;"),
                                Div(
                                    P("No payment methods", style="font-size: 14px; font-weight: 500;"),
                                    P("Add a card to enable automated recurring billing.", style="font-size: 12px; color: #94A3B8;"),
                                ),
                                style="display: flex; align-items: center;"
                            ),
                            cls="billing-card-body"
                        ),
                        Div(
                            Span(""),
                            Button("Add new card", cls="fav-create-btn", style="background: white; color: #1E293B; border: 1px solid #E2E8F0;"),
                            cls="billing-card-footer"
                        ),
                        cls="billing-card"
                    ),
                ),
                cls="billing-section"
            ),
            
            # 5. Credit Balance
            Div(
                Div("Credit Balance", cls="billing-section-title"),
                Div("Credits are applied to future invoices before charging your payment method.", cls="billing-section-desc"),
                Div(
                    Div(
                        Div(
                            Div("Balance", style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.04em;"),
                            Div(
                                Span("£", cls="credit-symbol"),
                                Span(f"{org.get('credit_balance', 0):,}", cls="credit-value"),
                                cls="credit-display"
                            ),
                            cls="billing-card-body"
                        ),
                        Div(
                            Button("Redeem Code", style="background: transparent; border: none; color: #64748B; font-size: 13px; cursor: pointer;"),
                            Form(
                                Button("Top Up →", type="submit", cls="fav-create-btn"),
                                action="/billing/checkout", method="post"
                            ),
                            cls="billing-card-footer"
                        ),
                        cls="billing-card"
                    ),
                ),
                cls="billing-section"
            ),
            
            # 6. Email Recipients
            Div(
                Div("Email Recipients", cls="billing-section-title"),
                Div("All billing correspondence will go to these email addresses.", cls="billing-section-desc"),
                Div(
                    Div(
                        Form(
                            Div(
                                Label("Primary Email", style="font-size: 12px; color: #94A3B8; display:block; margin-bottom: 4px;"),
                                Input(type="email", name="billing_email", value=org.get("billing_email", session.get('user', '')), 
                                      cls="fav-new-input", style="width: 100%; margin-bottom: 20px;"),
                                
                                Label("Additional Emails", style="font-size: 12px; color: #94A3B8; display:block; margin-bottom: 4px;"),
                                Textarea(name="additional_emails", placeholder="Separate multiple emails with commas", 
                                         cls="fav-new-input", style="width: 100%; min-height: 80px;"),
                            ),
                            Div(
                                Span("Emails will be CC'd on every invoice."),
                                Button("Save Settings", type="submit", cls="fav-create-btn"),
                                cls="billing-card-footer"
                            ),
                            hx_post="/billing/emails"
                        ),
                        cls="billing-card"
                    ),
                ),
                cls="billing-section"
            ),
            
            # 7. Billing Address
            Div(
                Div("Billing Address & Tax ID", cls="billing-section-title"),
                Div("Changes will be reflected in every upcoming invoice.", cls="billing-section-desc"),
                Div(
                    Div(
                        Form(
                            Div(
                                Label("Full Address", style="font-size: 12px; color: #94A3B8; display:block; margin-bottom: 4px;"),
                                Textarea(name="address", value=org.get("billing_address", ""),
                                         placeholder="Organisation Name\nStreet Address\nCity, Country",
                                         cls="fav-new-input", style="width: 100%; min-height: 100px; margin-bottom: 20px;"),
                                
                                Label("Tax ID", style="font-size: 12px; color: #94A3B8; display:block; margin-bottom: 4px;"),
                                Input(type="text", name="tax_id", value=org.get("tax_id", ""),
                                      placeholder="VAT / GST / EIN",
                                      cls="fav-new-input", style="width: 100%;"),
                            ),
                            Div(
                                Span("Required for registered businesses."),
                                Button("Save Address", type="submit", cls="fav-create-btn"),
                                cls="billing-card-footer"
                            ),
                            hx_post="/billing/address"
                        ),
                        cls="billing-card"
                    ),
                ),
                cls="billing-section"
            ),
            
            cls="billing-container"
        )
    )
