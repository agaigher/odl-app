from fasthtml.common import *

def SettingsKeys():

    # Mock Data for keys
    mock_keys = [
        {"name": "Production Server", "prefix": "odl_live_a7f...", "created": "2025-10-12", "last_used": "10 mins ago"},
        {"name": "Local Dev", "prefix": "odl_test_99b...", "created": "2025-11-05", "last_used": "2 days ago"}
    ]

    settings_style = Style("""
        .settings-header {
            margin-bottom: 32px;
        }
        .settings-title {
            font-size: 28px;
            font-weight: 700;
            margin: 0 0 8px 0;
            color: #F8FAFC;
        }
        .settings-subtitle {
            color: #94A3B8;
            margin: 0;
            font-size: 15px;
        }
        
        .settings-panel {
            background: #0F172A;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }
        .panel-title {
            font-size: 18px;
            font-weight: 600;
            color: #E2E8F0;
            margin: 0 0 16px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .keys-table {
            width: 100%;
            border-collapse: collapse;
        }
        .keys-table th {
            text-align: left;
            padding: 12px 0;
            color: #64748B;
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }
        .keys-table td {
            padding: 16px 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.05);
            color: #CBD5E1;
            font-size: 14px;
        }
        .keys-table tr:last-child td {
            border-bottom: none;
        }
        
        .key-name { font-weight: 500; color: #F8FAFC; }
        .key-prefix { font-family: 'Roboto Mono', monospace; font-size: 13px; color: #94A3B8; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px;}
        
        .action-icon {
            color: #64748B;
            cursor: pointer;
            transition: color 0.2s;
            background: none; border: none; font-size: 16px;
        }
        .action-icon:hover { color: #EF4444; }
    """)

    return Div(
        settings_style,
        Div(
            H1("API Keys", cls="settings-title"),
            P("Manage your API keys used to authenticate with OpenData.London HTTPS endpoints.", cls="settings-subtitle"),
            cls="settings-header"
        ),
        
        Div(
            Div(
                Span("Active Keys"),
                Button("+ Create new secret key", cls="odl-btn-primary"),
                cls="panel-title"
            ),
            Table(
                Thead(Tr(Th("Name"), Th("Key Prefix"), Th("Created"), Th("Last Used"), Th(""))),
                Tbody(
                    *[Tr(
                        Td(Span(key["name"], cls="key-name")),
                        Td(Span(key["prefix"], cls="key-prefix")),
                        Td(key["created"]),
                        Td(key["last_used"]),
                        Td(Button("🗑️", cls="action-icon", title="Revoke Key"))
                    ) for key in mock_keys]
                ),
                cls="keys-table"
            ),
            cls="settings-panel"
        )
    )

def SettingsShares():

    # Mock Data for snowflake shares
    mock_shares = [
        {"account": "XY12345.eu-west-1", "db": "LONDON_DATA", "status": "Active", "datasets": 45}
    ]

    return Div(
        Div(
            H1("Snowflake Secure Data Shares", style="font-size: 28px; font-weight: 700; margin: 0 0 8px 0; color: #F8FAFC;"),
            P("Provision zero-ETL access directly into your Snowflake account.", style="color: #94A3B8; margin: 0; font-size: 15px;"),
            style="margin-bottom: 32px;"
        ),
        
        Div(
            Div(
                Span("Configured Accounts", style="font-size: 18px; font-weight: 600; color: #E2E8F0;"),
                Button("+ Add Snowflake Account", cls="odl-btn-primary"),
                style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;"
            ),
            
            # Placeholder for listing accounts 
            *[Div(
                Div(
                    Div(
                        Span("❄", style="color: #29b5e8; font-size: 20px; margin-right: 12px;"),
                        Span("Account Locator: ", style="color: #64748B; font-size: 13px;"),
                        Span(share["account"], style="font-family: 'Roboto Mono', monospace; color: #F8FAFC; font-weight: 500; font-size: 16px;"),
                        style="display: flex; align-items: center;"
                    ),
                    Span(share["status"], style="background: rgba(34, 197, 94, 0.1); color: #4ADE80; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase;"),
                    style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;"
                ),
                Div(
                    Div(
                        Span("Target Database:", style="color: #64748B; font-size: 12px; display: block; margin-bottom: 4px;"),
                        Span(share["db"], style="font-family: 'Roboto Mono', monospace; color: #CBD5E1; font-size: 14px;"),
                    ),
                    Div(
                        Span("Authorized Datasets:", style="color: #64748B; font-size: 12px; display: block; margin-bottom: 4px;"),
                        Span(str(share["datasets"]), style="color: #CBD5E1; font-size: 14px; font-weight: 600;"),
                    ),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding: 16px; background: rgba(0,0,0,0.2); border-radius: 8px;"
                ),
                style="background: #0F172A; border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 12px; padding: 24px; margin-bottom: 16px;"
            ) for share in mock_shares]
        )
    )
