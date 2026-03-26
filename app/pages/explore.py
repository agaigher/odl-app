"""
Explore module page — data access options.
"""
from fasthtml.common import *

EXPLORE_STYLE = Style("""
    .explore-wrap {
        max-width: 1120px;
        margin: 0 auto;
        padding: 32px 24px 48px;
    }

    .explore-head {
        margin-bottom: 26px;
    }

    .explore-title {
        font-family: 'Space Grotesk', system-ui, sans-serif;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #F8FAFC;
        margin: 0 0 10px;
    }

    .explore-subtitle {
        margin: 0;
        max-width: 760px;
        color: #94A3B8;
        font-size: 15px;
        line-height: 1.7;
    }

    .explore-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 14px;
    }

    .explore-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px;
        min-height: 162px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        transition: border-color 0.15s, transform 0.15s, background 0.15s;
    }

    .explore-card:hover {
        border-color: rgba(56,189,248,0.35);
        background: rgba(56,189,248,0.07);
        transform: translateY(-1px);
    }

    .explore-card-title {
        margin: 0;
        color: #E2E8F0;
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    .explore-card-desc {
        margin: 0;
        color: #94A3B8;
        font-size: 13px;
        line-height: 1.55;
        flex: 1;
    }

    .explore-tag-row {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
    }

    .explore-tag {
        font-size: 11px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.14);
        color: #CBD5E1;
        padding: 4px 8px;
        background: rgba(255,255,255,0.02);
    }
""")


def _access_card(title, description, tags):
    return Div(
        H3(title, cls="explore-card-title"),
        P(description, cls="explore-card-desc"),
        Div(*[Span(tag, cls="explore-tag") for tag in tags], cls="explore-tag-row"),
        cls="explore-card"
    )


def ExploreChat():
    """Data access options for developers and non-technical users."""
    access_methods = [
        (
            "SQL Query Workspace",
            "Run SQL directly in the browser for ad-hoc analysis, validation, and quick joins.",
            ["Developers", "Analysts"],
        ),
        (
            "AI Data Assistant Chat",
            "Ask questions in plain language and get relevant tables, filters, and suggested queries.",
            ["Non-technical", "Analysts"],
        ),
        (
            "Graph API Endpoint",
            "Integrate graph-based queries into apps and workflows using a structured API interface.",
            ["Developers", "Applications"],
        ),
        (
            "Snowflake Secure Share",
            "Consume curated datasets in your Snowflake environment without copying raw source files.",
            ["Data teams", "Enterprise"],
        ),
        (
            "Export to File (Download)",
            "Download filtered results as CSV or JSON for local analysis and offline sharing.",
            ["Everyone", "Portable"],
        ),
        (
            "MCP Server Access",
            "Connect data to AI agents and tools through a Model Context Protocol server.",
            ["Developers", "AI workflows"],
        ),
        (
            "REST API Endpoint",
            "Use HTTP endpoints for automation, custom apps, and integration with backend services.",
            ["Developers", "Automation"],
        ),
        (
            "Business Intelligence Connectors",
            "Plug into Power BI, Tableau, or Looker for dashboards and stakeholder reporting.",
            ["Analysts", "Business users"],
        ),
        (
            "Spreadsheet Access",
            "Open data in Excel or Google Sheets for lightweight analysis and familiar workflows.",
            ["Non-technical", "Ops teams"],
        ),
        (
            "Scheduled Reports",
            "Deliver recurring snapshots to teams by email to keep non-technical users updated.",
            ["Business users", "Operations"],
        ),
    ]

    return Div(
        EXPLORE_STYLE,
        Div(
            H1("Choose How You Access Data", cls="explore-title"),
            P(
                "Use the access path that best fits your workflow, from no-code reporting and "
                "spreadsheets to APIs, SQL, and AI-native integrations.",
                cls="explore-subtitle"
            ),
            cls="explore-head"
        ),
        Div(
            *[_access_card(title, description, tags) for title, description, tags in access_methods],
            cls="explore-grid"
        ),
        cls="explore-wrap"
    )
