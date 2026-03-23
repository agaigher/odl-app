from fasthtml.common import *
from app.supabase_db import db_select
from app.components import icon_svg, IC

def BillingDashboard(user_id="", session=None):
    # Get active organization context
    try:
        from app.supabase_db import db_select
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships:
            return Div("You are not part of any organization.", cls="error-text", style="padding: 40px; text-align: center;")
            
        org_id = memberships[0]["org_id"]
        orgs = db_select("organisations", {"id": org_id})
        org = orgs[0] if orgs else {}
        ledger = db_select("billing_ledger", {"org_id": org_id}, order="created_at.desc", limit=5)
    except Exception as e:
        return Div(f"Error loading billing: {e}", cls="error-text")

    BILLING_STYLE = Style("""
        .billing-top-header { padding: 40px 0 20px; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .billing-page-title { font-size: 24px; font-weight: 700; color: #F8FAFC; margin: 0; }
        
        .billing-grid {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 60px;
            padding: 48px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .billing-grid:last-child { border-bottom: none; }
        
        .info-col h2 { font-size: 16px; font-weight: 600; color: #F8FAFC; margin-bottom: 8px; }
        .info-col p { font-size: 13px; color: #94A3B8; line-height: 1.5; margin: 0; }
        
        .card-col { max-width: 800px; }
        .billing-card {
            background: #111827;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            overflow: hidden;
        }
        .card-main { padding: 24px; }
        .card-footer { 
            padding: 16px 24px; 
            background: rgba(255,255,255,0.02); 
            border-top: 1px solid rgba(255,255,255,0.06);
            display: flex; justify-content: space-between; align-items: center;
        }
        
        .plan-title { font-size: 28px; font-weight: 700; color: #10B981; margin-bottom: 24px; }
        .usage-notice {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 16px;
            display: flex; gap: 16px;
        }
        .notice-icon { color: #94A3B8; flex-shrink: 0; padding-top: 2px; }
        .notice-text { font-size: 13px; color: #F8FAFC; line-height: 1.5; }
        .notice-sub { color: #94A3B8; display: block; margin-top: 4px; }
        
        .spend-cap-card { display: flex; align-items: center; gap: 16px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 20px; }
        .spend-cap-info h3 { font-size: 14px; font-weight: 600; color: #F8FAFC; margin: 0; }
        .spend-cap-info p { font-size: 12px; color: #94A3B8; margin: 4px 0 0; }
        
        /* Table Styles */
        .invoice-table { width: 100%; border-collapse: collapse; }
        .invoice-table th { text-align: left; font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .invoice-table td { padding: 16px; font-size: 13px; color: #F1F5F9; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle; }
        .status-pill { font-size: 10px; font-weight: 700; color: #10B981; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }
        
        .paginator { padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #475569; }
        .pag-btns { display: flex; gap: 4px; }
        .pag-btn { background: transparent; border: 1px solid rgba(255,255,255,0.06); color: #94A3B8; padding: 4px; border-radius: 4px; cursor: pointer; }
        
        .balance-hero { display: flex; justify-content: space-between; align-items: baseline; }
        .balance-label { font-size: 16px; font-weight: 600; color: #F8FAFC; }
        .balance-value { font-size: 32px; font-weight: 700; color: #F8FAFC; }
        .balance-value span { font-size: 18px; color: #475569; margin-right: 4px; }
        
        .billing-input {
            width: 100%;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 6px;
            color: #F8FAFC;
            padding: 10px 12px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s;
        }
        .billing-input:focus { border-color: #0284C7; }
        .billing-label { display: block; font-size: 13px; font-weight: 600; color: #F8FAFC; margin-bottom: 8px; }
        .billing-label.muted { color: #94A3B8; font-weight: 400; margin-top: 12px; }
        
        .btn-black { background: #1F2937; color: #F8FAFC; border: 1px solid rgba(255,255,255,0.1); padding: 7px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; }
        .btn-green { background: #10B981; color: #ffffff; border: none; padding: 7px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; }
        .btn-outline { background: transparent; color: #94A3B8; border: 1px solid rgba(255,255,255,0.08); padding: 7px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; }
        
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
    """)

    def billing_section(title, desc, *content):
        return Div(
            Div(H2(title), P(desc), cls="info-col"),
            Div(*content, cls="card-col"),
            cls="billing-grid"
        )

    return Div(
        BILLING_STYLE,
        Div(
            Div(H1("Billing", cls="billing-page-title"), cls="billing-top-header"),
            
            # 1. Subscription Plan
            billing_section(
                "Subscription Plan",
                "Each organization has it's own subscription plan, billing cycle, payment methods and usage quotas.",
                Div(
                    Div(
                        Div("Free Plan", cls="plan-title"),
                        Button("Change subscription plan", cls="btn-black"),
                        Div(
                            Div(icon_svg(IC.info), cls="notice-icon"),
                            Div(
                                Span("This organization is limited by the included usage", style="font-weight: 600;"),
                                Span("Projects may become unresponsive when this organization exceeds its included usage quota. To scale seamlessly, upgrade to a paid plan.", cls="notice-sub"),
                                cls="notice-text"
                            ),
                            cls="usage-notice", style="margin-top: 32px;"
                        ),
                        cls="card-main"
                    ),
                    cls="billing-card"
                )
            ),
            
            # 2. Cost Control
            billing_section(
                "Cost Control",
                "Allow scaling beyond your plan's included quota.\n\nMore information\nSpend cap",
                Div(
                    Div(
                        Div(
                            P("If you need to go beyond the included quota, simply switch off your spend cap to pay for additional usage.", style="font-size: 13px; color: #94A3B8; margin-bottom: 24px;"),
                            Div(
                                Div(style="width: 120px; height: 80px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: flex-end; gap: 4px; padding: 8px;"),
                                Div(
                                    Div(
                                        H3("Spend cap is enabled"),
                                        P("You won't be charged any extra for usage. However, your projects could become unresponsive or enter read only mode if you exceed the included quota."),
                                        cls="spend-cap-info"
                                    ),
                                    Button("Change spend cap", cls="btn-black", style="margin-top: 16px;"),
                                    style="flex: 1;"
                                ),
                                style="display: flex; gap: 24px; align-items: flex-start;"
                            ),
                            cls="card-main"
                        ),
                        cls="billing-card"
                    )
                )
            ),
            
            # 3. Past Invoices
            billing_section(
                "Past Invoices",
                "You get an invoice every time you change your plan or when your monthly billing cycle resets.",
                Div(
                    Div(
                        Table(
                            Thead(Tr(Th(""), Th("Date"), Th("Amount"), Th("Invoice Number"), Th("Status"), Th(""))),
                            Tbody(
                                *[Tr(
                                    Td(icon_svg(IC.file_text, style="opacity: 0.3;")),
                                    Td(i["created_at"].strftime("%b %d, %Y") if hasattr(i["created_at"], "strftime") else str(i["created_at"])[:12]),
                                    Td(f"${float(i.get('amount_paid', 0)):,.2f}"),
                                    Td(str(i.get("stripe_session_id", "INV-000"))[:12], style="font-family: 'Roboto Mono', monospace; color: #64748B;"),
                                    Td(Span("Paid", cls="status-pill")),
                                    Td(icon_svg(IC.external_link, style="opacity: 0.3; cursor: pointer;")),
                                ) for i in ledger] if ledger else [
                                    Tr(Td(icon_svg(IC.file_text, style="opacity: 0.3;")), Td("Mar 20, 2026"), Td("$0.00"), Td("JXTTCH-00018", style="font-family: 'Roboto Mono', monospace; color: #64748B;"), Td(Span("Paid", cls="status-pill")), Td(icon_svg(IC.external_link, style="opacity: 0.3; cursor: pointer;"))),
                                    Tr(Td(icon_svg(IC.file_text, style="opacity: 0.3;")), Td("Feb 20, 2026"), Td("$0.00"), Td("JXTTCH-00017", style="font-family: 'Roboto Mono', monospace; color: #64748B;"), Td(Span("Paid", cls="status-pill")), Td(icon_svg(IC.external_link, style="opacity: 0.3; cursor: pointer;")))
                                ]
                            ),
                            cls="invoice-table"
                        ),
                        Div(
                            Span("Showing 1 to 5 out of 23 invoices"),
                            Div(
                                Button(icon_svg(IC.chevron_left), cls="pag-btn"),
                                Button(icon_svg(IC.chevron_right), cls="pag-btn"),
                                cls="pag-btns"
                            ),
                            cls="paginator"
                        ),
                        cls="billing-card"
                    )
                )
            ),
            
            # 4. Payment Methods
            billing_section(
                "Payment Methods",
                "Payments for your subscription are made using the default card.",
                Div(
                    Div(
                        Div(
                            Div(
                                icon_svg(IC.credit_card, style="opacity: 0.5; margin-right: 12px;"),
                                P("No payment methods", style="font-size: 13px; color: #94A3B8; margin: 0;"),
                                style="display: flex; align-items: center; padding: 20px 0 40px;"
                            ),
                            cls="card-main"
                        ),
                        Div(
                            Span(""),
                            Button("+ Add new card", cls="btn-black"),
                            cls="card-footer"
                        ),
                        cls="billing-card"
                    )
                )
            ),
            
            # 5. Credit Balance
            billing_section(
                "Credit Balance",
                "Credits will be applied to future invoices, before charging your payment method. If your credit balance runs out, your default payment method will be charged.",
                Div(
                    Div(
                        Div(
                            Div(
                                Span("Balance", cls="balance-label"),
                                Div(Span("$"), Span(f"{float(org.get('credit_balance', 0)):.2f}"), cls="balance-value"),
                                cls="balance-hero"
                            ),
                            cls="card-main"
                        ),
                        Div(
                            Span(""),
                            Div(
                                Button("Redeem Code", cls="btn-outline", style="margin-right: 8px;"),
                                Button("Top Up", cls="btn-outline"),
                            ),
                            cls="card-footer"
                        ),
                        cls="billing-card"
                    )
                )
            ),
            
            # 6. Email Recipient
            billing_section(
                "Email Recipient",
                "All billing correspondence will go to this email",
                Div(
                    Div(
                        Form(
                            Div(
                                Label("Email address", cls="billing-label"),
                                Input(type="email", name="billing_email", value=org.get("billing_email", ""), cls="billing-input"),
                                Label("Additional emails", cls="billing-label muted"),
                                Input(placeholder="Add additional recipients", name="additional_emails", value=org.get("additional_billing_emails", ""), cls="billing-input"),
                                cls="card-main"
                            ),
                            Div(
                                Span(""),
                                Div(
                                    Button("Cancel", cls="btn-outline", style="margin-right: 8px;", type="button"),
                                    Button("Save", cls="btn-green", type="submit"),
                                ),
                                cls="card-footer"
                            ),
                            hx_post="/billing/emails"
                        ),
                        cls="billing-card"
                    )
                )
            ),
            
            # 7. Billing Address & Tax ID
            billing_section(
                "Billing Address & Tax ID",
                "Changes will be reflected in every upcoming invoice, past invoices are not affected\n\nA Tax ID is only required for registered businesses.",
                Div(
                    Div(
                        Form(
                            Div(
                                Label("Name", cls="billing-label"),
                                Input(name="billing_name", value=org.get("billing_name", ""), cls="billing-input", style="margin-bottom: 20px;"),
                                
                                Label("Address line 1", cls="billing-label"),
                                Input(name="billing_address_line1", value=org.get("billing_address_line1", ""), placeholder="123 Main Street", cls="billing-input", style="margin-bottom: 20px;"),
                                
                                Label("Address line 2 (optional)", cls="billing-label"),
                                Input(name="billing_address_line2", value=org.get("billing_address_line2", ""), placeholder="Apartment, suite, unit, building, floor, etc.", cls="billing-input", style="margin-bottom: 20px;"),
                                
                                Div(
                                    Div(
                                        Label("Country", cls="billing-label"),
                                        Select(
                                            Option("Select country", value=""),
                                            Option("United Kingdom", value="UK"),
                                            Option("United States", value="US"),
                                            name="billing_country", cls="billing-input"
                                        ),
                                    ),
                                    Div(
                                        Label("Postal code", cls="billing-label"),
                                        Input(name="billing_postal_code", value=org.get("billing_postal_code", ""), placeholder="12345", cls="billing-input"),
                                    ),
                                    cls="form-row"
                                ),
                                
                                Div(
                                    Div(
                                        Label("City", cls="billing-label"),
                                        Input(name="billing_city", value=org.get("billing_city", ""), cls="billing-input"),
                                    ),
                                    Div(
                                        Label("State / Province", cls="billing-label"),
                                        Input(name="billing_state", value=org.get("billing_state", ""), cls="billing-input"),
                                    ),
                                    cls="form-row", style="margin-top: 16px;"
                                ),
                                
                                Label("Business Tax ID", cls="billing-label", style="margin-top: 20px;"),
                                Select(
                                    Option("Select tax ID", value=""),
                                    Option("VAT", value="VAT"),
                                    Option("EIN", value="EIN"),
                                    name="billing_tax_id_type", cls="billing-input"
                                ),
                                cls="card-main"
                            ),
                            Div(
                                Span(""),
                                Div(
                                    Button("Cancel", cls="btn-outline", style="margin-right: 8px;", type="button"),
                                    Button("Save", cls="btn-green", type="submit"),
                                ),
                                cls="card-footer"
                            ),
                            hx_post="/billing/address"
                        ),
                        cls="billing-card"
                    )
                )
            ),
            
            style="max-width: 1200px; margin: 0 auto; padding: 0 40px 100px;"
        )
    )
