from fasthtml.common import *
from app.components import odl_navbar, odl_sidebar

def get_app_style():
    # Base application styling
    return Style("""
        :root {
            --bg-page: #0F172A;
            --bg-surface: #1E293B;
            --bg-card: #1E293B;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --text-faint: #475569;
            --accent: #0284C7;
            --accent-light: rgba(2, 132, 199, 0.15);
            --border: rgba(255, 255, 255, 0.05);
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
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
    
