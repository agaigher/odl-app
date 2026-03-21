from fasthtml.common import *
from app.db import datasets_tbl

def DatasetDetail(slug: str):
    
    # Simple lookup
    dataset = None
    for ds in datasets_tbl():
        if ds['slug'] == slug:
            dataset = ds
            break
            
    if not dataset:
        return Div(
            H1("Dataset Not Found", style="color: #F8FAFC;"),
            P("The requested dataset does not exist or you do not have permission to view it.", style="color: #94A3B8;"),
            A("← Back to Catalog", href="/", style="color: #29b5e8; text-decoration: none;")
        )

    detail_style = Style("""
        .detail-header {
            margin-bottom: 40px;
            padding-bottom: 24px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.15);
        }
        .back-link {
            color: #64748B;
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 24px;
            transition: color 0.2s;
        }
        .back-link:hover {
            color: #F8FAFC;
        }
        .dataset-title {
            font-size: 32px;
            font-weight: 700;
            color: #F8FAFC;
            margin: 0 0 12px 0;
            letter-spacing: -0.5px;
        }
        
        .layout-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 40px;
            align-items: start;
        }
        
        .section-title {
            font-size: 16px;
            font-weight: 600;
            color: #E2E8F0;
            margin-bottom: 16px;
            font-family: 'Roboto Mono', monospace;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 40px;
        }
        
        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: #0F172A;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 24px;
        }
        .data-table th {
            text-align: left;
            padding: 12px 16px;
            background: rgba(0, 0, 0, 0.2);
            color: #94A3B8;
            font-weight: 500;
            font-size: 13px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.15);
            white-space: nowrap;
        }
        .data-table td {
            padding: 12px 16px;
            color: #CBD5E1;
            font-size: 14px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.05);
        }
        .data-table tr:last-child td {
            border-bottom: none;
        }
        .type-badge {
            background: rgba(41, 181, 232, 0.1);
            color: #29b5e8;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Roboto Mono', monospace;
            font-size: 12px;
        }
        
        /* Data Quality Metrics */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .metric-card {
            background: #0F172A;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            flex-direction: column;
        }
        .metric-label {
            color: #64748B;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .metric-value {
            color: #F8FAFC;
            font-size: 24px;
            font-weight: 700;
            font-family: 'Roboto Mono', monospace;
        }
        .metric-status {
            margin-top: 8px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-good { color: #10B981; }
        .status-warn { color: #F59E0B; }
        
        /* Sidebar Panel */
        .info-panel {
            background: #0F172A;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 12px;
            padding: 24px;
            position: sticky;
            top: 24px;
        }
        .info-row {
            margin-bottom: 16px;
        }
        .info-row:last-child {
            margin-bottom: 0;
        }
        .info-label {
            color: #64748B;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }
        .info-value {
            color: #F8FAFC;
            font-size: 14px;
            font-weight: 500;
        }
        
        /* Code Block */
        .code-block {
            background: #020617;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid rgba(148, 163, 184, 0.15);
            font-family: 'Roboto Mono', monospace;
            font-size: 13px;
            color: #38BDF8;
            overflow-x: auto;
            white-space: pre-wrap;
            line-height: 1.5;
            margin-bottom: 24px;
        }
        .code-keyword { color: #E879F9; }
        .code-string { color: #A3E635; }
    """)

    # Mock schema and sample data based on slug
    schema_rows = []
    sample_headers = []
    sample_data = []
    metrics = []

    if dataset['slug'] == "uk-companies-house":
        schema_rows = [
            ("company_number", "VARCHAR", "Primary Unique Identifier"),
            ("company_name", "VARCHAR", "Registered name of the entity"),
            ("company_status", "VARCHAR", "Active, Dissolved, Liquidation, etc."),
            ("incorporation_date", "DATE", "Date of formation"),
            ("sic_codes", "ARRAY", "Standard Industrial Classification"),
            ("registered_address", "JSON", "Structured address payload")
        ]
        sample_headers = ["company_number", "company_name", "company_status", "incorporation_date"]
        sample_data = [
            ["00000006", "ANGLO-SCOTTISH BEET SUGAR CORPORATION LIMITED", "Dissolved", "1923-01-25"],
            ["00000018", "TUDOR ENGINEERING COMPANY LIMITED", "Active", "1856-07-29"],
            ["00000043", "BAKER HUGHES LIMITED", "Active", "1856-09-02"],
        ]
        metrics = [
            {"label": "Total Rows", "value": "5.4M+", "status": "Updated today", "cls": "status-good"},
            {"label": "Completeness", "value": "99.8%", "status": "No missing IDs", "cls": "status-good"},
            {"label": "Freshness", "value": "12 hrs", "status": "Slight delay", "cls": "status-warn"}
        ]
    elif dataset['slug'] == "tfl-transport-network":
         schema_rows = [
            ("incident_id", "VARCHAR", "Unique ID"),
            ("line_id", "VARCHAR", "e.g., victoria, central"),
            ("status_severity", "INT", "Numeric severity scale"),
            ("status_description", "VARCHAR", "Human readable status"),
            ("created_at", "TIMESTAMP", "Event time")
        ]
         sample_headers = ["incident_id", "line_id", "status_severity", "status_description"]
         sample_data = [
             ["evt_9812", "victoria", "10", "Good Service"],
             ["evt_9813", "central", "7", "Minor Delays"],
             ["evt_9814", "bakerloo", "10", "Good Service"],
         ]
         metrics = [
            {"label": "Total Rows", "value": "12.1M+", "status": "Real-time sync", "cls": "status-good"},
            {"label": "Completeness", "value": "100%", "status": "Perfect schema", "cls": "status-good"},
            {"label": "Freshness", "value": "< 1 min", "status": "Live stream", "cls": "status-good"}
        ]
    else:
        schema_rows = [
            ("id", "VARCHAR", "Primary Key"),
            ("data_blob", "JSON", "Flexible payload"),
            ("updated_at", "TIMESTAMP", "Last modified")
        ]
        sample_headers = ["id", "updated_at"]
        sample_data = [
            ["gen_001", "2026-03-08 10:00:00"],
            ["gen_002", "2026-03-08 10:05:00"],
        ]
        metrics = [
            {"label": "Total Rows", "value": "Unknown", "status": "Pending eval", "cls": "status-warn"},
            {"label": "Completeness", "value": "N/A", "status": "Schema variant", "cls": "status-warn"},
            {"label": "Freshness", "value": "N/A", "status": "Batch sync", "cls": "status-warn"}
        ]

    return Div(
        detail_style,
        A("← Catalog", href="/", cls="back-link"),
        
        Div(
            H1(dataset['name'], cls="dataset-title"),
            P(dataset['description'], style="color: #94A3B8; font-size: 16px; max-width: 800px; line-height: 1.6;"),
            cls="detail-header"
        ),
        
        Div(
            # Main Content (Schema, Metrics, Samples)
            Div(
                H2("Table Schema", cls="section-title", style="margin-top: 0;"),
                Table(
                    Thead(Tr(Th("Column Name"), Th("Data Type"), Th("Description"))),
                    Tbody(
                        *[Tr(
                            Td(Span(row[0], style="font-weight: 500; font-family: 'Roboto Mono', monospace;")), 
                            Td(Span(row[1], cls="type-badge")), 
                            Td(row[2])
                        ) for row in schema_rows]
                    ),
                    cls="data-table"
                ),
                
                H2("Data Quality Metrics", cls="section-title"),
                Div(
                    *[Div(
                        Div(m['label'], cls="metric-label"),
                        Div(m['value'], cls="metric-value"),
                        Div(m['status'], cls=f"metric-status {m['cls']}"),
                        cls="metric-card"
                    ) for m in metrics],
                    cls="metrics-grid"
                ),
                
                H2("Sample Rows", cls="section-title"),
                Div(
                     Table(
                        Thead(Tr(*[Th(h) for h in sample_headers])),
                        Tbody(
                            *[Tr(*[Td(cell) for cell in row]) for row in sample_data]
                        ),
                        cls="data-table"
                    ),
                    style="overflow-x: auto;"
                ),
                
                H2("Query Example (Snowflake)", cls="section-title"),
                Pre(
                    Code(
                        Span("SELECT", cls="code-keyword"), " * ", 
                        Span("FROM", cls="code-keyword"), " LONDON_DATA.PUBLIC.", dataset['slug'].replace("-", "_").upper(), "\n",
                        Span("WHERE", cls="code-keyword"), " updated_at > DATEADD(day, -1, CURRENT_DATE())\n",
                        Span("LIMIT", cls="code-keyword"), " 100;",
                        cls="code-block"
                    )
                )
            ),
            
            # Sidebar Info
            Div(
                Div(
                    Div(
                        Div("Provider", cls="info-label"),
                        Div(dataset['provider'], cls="info-value"),
                        cls="info-row"
                    ),
                    Div(
                        Div("Category", cls="info-label"),
                        Div(dataset['category'], cls="info-value"),
                        cls="info-row"
                    ),
                    Div(
                        Div("Update Frequency", cls="info-label"),
                        Div(dataset['update_frequency'], cls="info-value"),
                        cls="info-row"
                    ),
                    Div(
                        Div("Snowflake Database", cls="info-label"),
                        Div("LONDON_DATA", cls="info-value", style="font-family: 'Roboto Mono', monospace; font-size: 13px;"),
                        cls="info-row"
                    ),
                    A("Provision Access", href=f"/shares?dataset={dataset['slug']}", cls="odl-btn-primary", style="display: block; text-align: center; margin-top: 24px; text-decoration: none;"),
                    cls="info-panel"
                )
            ),
            
            cls="layout-grid"
        )
    )
