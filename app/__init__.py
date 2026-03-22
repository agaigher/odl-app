from fasthtml.common import *
from app.components import odl_navbar, odl_sidebar

def get_app_style():
    # Base application styling
    return Style("""
        :root {
            --bg-page: #F1F5F9;
            --bg-surface: #FFFFFF;
            --bg-card: #FFFFFF;
            --text-main: #1E293B;
            --text-muted: #64748B;
            --text-faint: #94A3B8;
            --accent: #0284C7;
            --accent-light: #E0F2FE;
            --border: #E2E8F0;
            --shadow: 0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }

        *, *::before, *::after { box-sizing: border-box; }

        body.app-layout {
            background-color: var(--bg-page);
            color: var(--text-main);
            font-family: 'Inter', system-ui, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        .app-container {
            display: flex;
            flex: 1;
            height: calc(100vh - 60px);
            overflow: hidden;
        }

        .main-content {
            flex: 1;
            padding: 32px 48px;
            overflow-y: auto;
            background: var(--bg-page);
        }

        /* Forms & Inputs */
        input.odl-input, select.odl-input {
            width: 100%;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 12px 16px;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            margin-bottom: 16px;
        }

        input.odl-input:focus, select.odl-input:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(2,132,199,0.12);
        }

        button.odl-btn-primary {
            background: var(--accent);
            color: #ffffff;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }

        button.odl-btn-primary:hover {
            background: #0369A1;
        }

        .success-text { color: #16A34A; font-size: 14px; }
        .error-text   { color: #DC2626; font-size: 14px; }
    """)
    
