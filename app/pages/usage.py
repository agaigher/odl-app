from fasthtml.common import *
from app.supabase_db import db_select
from app.components import icon_svg, IC

def UsageDashboard(user_id="", session=None):
    # Get active organization context
    try:
        from app.supabase_db import db_select
        memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
        if not memberships:
            return Div("You are not part of any organization.", cls="error-text", style="padding: 40px; text-align: center;")
            
        org_id = memberships[0]["org_id"]
        orgs = db_select("organisations", {"id": org_id})
        org = orgs[0] if orgs else {}
        
        # Get active project (for per-project usage)
        active_project_id = session.get('active_project_id')
        projects = db_select("projects", {"org_id": org_id})
        active_project = next((p for p in projects if str(p["id"]) == str(active_project_id)), projects[0] if projects else None)
        
    except Exception as e:
        return Div(f"Error loading usage: {e}", cls="error-text")

    USAGE_STYLE = Style("""
        .usage-header { padding: 40px 0 24px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 48px; }
        .usage-title { font-size: 24px; font-weight: 700; color: #F8FAFC; margin-bottom: 24px; }
        .usage-controls { display: flex; justify-content: space-between; align-items: center; }
        .control-group { display: flex; gap: 8px; }
        
        .plan-info { font-size: 13px; color: #94A3B8; }
        .plan-highlight { color: #10B981; font-weight: 600; }
        
        /* Summary Grid */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 60px;
        }
        .summary-item {
            background: #080a0f;
            padding: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .metric-info h3 { font-size: 13px; font-weight: 500; color: #F8FAFC; margin: 0 0 6px 0; display: flex; align-items: center; gap: 4px; }
        .metric-info p { font-size: 12px; color: #94A3B8; margin: 0; }
        .metric-value { font-size: 13px; font-weight: 600; color: #F8FAFC; margin-top: 4px; }
        
        .progress-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 3px solid rgba(255,255,255,0.05);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .progress-fill {
            position: absolute;
            inset: -3px;
            border-radius: 50%;
            border: 3px solid transparent;
            border-top-color: #0284C7;
            transform: rotate(45deg);
        }
        
        /* Section Layout */
        .usage-section {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 60px;
            padding: 48px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .usage-section:last-child { border-bottom: none; }
        
        .info-col h2 { font-size: 18px; font-weight: 600; color: #F8FAFC; margin: 0 0 12px 0; }
        .info-col p { font-size: 13px; color: #94A3B8; line-height: 1.6; margin: 0 0 20px 0; }
        .more-info-link { font-size: 12px; color: #94A3B8; text-decoration: none; display: flex; align-items: center; gap: 4px; margin-top: 8px; }
        .more-info-link:hover { color: #F8FAFC; }
        
        .card-col { max-width: 800px; }
        .usage-card {
            background: #111827;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            overflow: hidden;
        }
        .card-main { padding: 24px; }
        
        .usage-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        .usage-table tr { border-top: 1px solid rgba(255,255,255,0.04); }
        .usage-table tr:first-child { border-top: none; }
        .usage-table td { padding: 12px 0; font-size: 13px; color: #94A3B8; }
        .usage-table td:last-child { text-align: right; color: #F1F5F9; font-weight: 600; }
        
        .chart-placeholder {
            margin-top: 32px;
            height: 160px;
            background: rgba(255,255,255,0.01);
            border: 1px dashed rgba(255,255,255,0.1);
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #475569;
            font-size: 12px;
            gap: 12px;
        }
        
        .btn-upgrade {
            background: #10B981; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;
        }
        .tag-unavailable { font-size: 11px; font-weight: 700; color: #EF4444; background: rgba(239,68,68,0.1); padding: 2px 6px; border-radius: 4px; text-transform: uppercase; }
        
        .usage-select {
            background: #0F172A;
            border: 1px solid rgba(255,255,255,0.1);
            color: #CBD5E1;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            outline: none;
            cursor: pointer;
        }
    """)

    def summary_item(title, value, subtext, percentage=0, upgrade=False):
        return Div(
            Div(
                H3(title, Span(icon_svg(IC.chevron_right, style="width: 12px; height: 12px; opacity: 0.5;"))),
                Div(value, cls="metric-value"),
                P(subtext),
                cls="metric-info"
            ),
            Div(
                Button("Upgrade", cls="btn-upgrade") if upgrade else 
                Div(Div(cls="progress-fill", style=f"transform: rotate({percentage*3.6}deg);"), cls="progress-circle"),
                style="display: flex; align-items: center;"
            ),
            cls="summary-item"
        )

    def usage_detail_section(title, desc, included, used, overage, more_info_url="#"):
        return Div(
            Div(
                H2(title),
                P(desc),
                A("More information", href=more_info_url, cls="more-info-link"),
                A("Documentation", href="#", cls="more-info-link", style="margin-top: 4px;"),
                cls="info-col"
            ),
            Div(
                Div(
                    Div(
                        H3(f"{title} usage", style="font-size: 14px; font-weight: 600; color: #F8FAFC; margin-bottom: 20px;"),
                        Table(
                            Tr(Td("Included in Free Plan"), Td(included)),
                            Tr(Td("Used in period"), Td(used)),
                            Tr(Td("Overage in period"), Td(overage)),
                            cls="usage-table"
                        ),
                        Div(
                            icon_svg(IC.chart, style="opacity: 0.2; width: 48px; height: 48px;"),
                            P("No data in period"),
                            P("May take up to 24 hours to show", style="font-size: 11px; opacity: 0.5; margin-top: -8px;"),
                            cls="chart-placeholder"
                        ),
                        cls="card-main"
                    ),
                    cls="usage-card"
                ),
                cls="card-col"
            ),
            cls="usage-section"
        )

    return Div(
        USAGE_STYLE,
        Div(
            # Header
            Div(
                H1("Usage", cls="usage-title"),
                Div(
                    Div(
                        Select(Option("Current billing cycle"), cls="usage-select"),
                        Select(
                            Option("All projects", value="all"),
                            *[Option(p["name"], value=p["id"]) for p in projects],
                            cls="usage-select"
                        ),
                        cls="control-group"
                    ),
                    Div(
                        Span("Organization is on the ", cls="plan-info"),
                        Span("Free Plan", cls="plan-highlight"),
                        Span(" / 20 Mar 2026 - 20 Apr 2026", cls="plan-info"),
                        cls="plan-info"
                    ),
                    cls="usage-controls"
                ),
                cls="usage-header"
            ),
            
            # Summary Grid
            Div(
                summary_item("API Requests", "12,450 / 50,000", "24.9% of quota used", 24.9),
                summary_item("Snowflake Zero Copy", "8 / 10 Shares", "80% of quota used", 80),
                summary_item("Database Size", "29.25 MB / 0.5 GB", "5.8% of quota used", 5.8),
                summary_item("Egress", "0.05 GB / 5 GB", "1% of quota used", 1),
                summary_item("Monthly Active Users", "1 / 50,000 MAU", "<1% of quota", 1),
                summary_item("Monthly Active SSO Users", "Unavailable in plan", "Requires upgrade", upgrade=True),
                summary_item("Storage Size", "0 / 1 GB", "0% of quota used", 0),
                summary_item("Realtime Concurrent Peak", "0 / 200", "0% of quota used", 0),
                summary_item("Realtime Messages", "0 / 2,000,000", "0% of quota used", 0),
                summary_item("Edge Function Invocations", "0 / 500,000", "0% of quota used", 0),
                summary_item("Storage Image Transformations", "Unavailable in plan", "Requires upgrade", upgrade=True),
                summary_item("Monthly Active Third-Party Users", "0 / 50,000 MAU", "0% of quota", 0),
                cls="summary-grid"
            ),
            
            # API Usage (Detailed)
            usage_detail_section(
                "API Requests",
                "Total requests to the Open Data API and Snowflake proxy throughout the billing period.",
                "50,000 Requests", "12,450", "0"
            ),
            
            # snowflake
            usage_detail_section(
                "Snowflake Zero Copy",
                "Number of shared datasets active in your Snowflake account via Zero Copy integration.",
                "10 Shares", "8", "0"
            ),
            
            # Edge Functions
            usage_detail_section(
                "Edge Function Invocations",
                "Every serverless function invocation independent of response status is counted.",
                "500,000", "0", "0"
            ),
            
            # Realtime
            usage_detail_section(
                "Realtime Messages",
                "Count of messages going through Realtime. Includes database changes, broadcast and presence.",
                "2,000,000", "0", "0"
            ),
            
            style="max-width: 1200px; margin: 0 auto; padding: 0 40px 100px;"
        )
    )
