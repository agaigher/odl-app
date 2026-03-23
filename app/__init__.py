from fasthtml.common import *
from app.components import odl_navbar, odl_sidebar

def get_app_style():
    # Base application styling — shared OpenData.London palette (aligned with odl-web marketing site)
    return Style("""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap');

        :root {
            --font-display: "Space Grotesk", system-ui, sans-serif;
            --font-body: "Inter", system-ui, sans-serif;
            --font-mono: "JetBrains Mono", ui-monospace, monospace;
            /* Canvas (slate) — deep, minimal */
            --bg-page: #080a0f;
            --bg-elevated: #0f1118;
            --bg-surface: #141824;
            --bg-card: #161a2a;
            --bg-muted: #0c1018;
            /* Text */
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --text-faint: #475569;
            /* Light surfaces (cards, modals, catalog on dark shell) */
            --surface-light: #FFFFFF;
            --text-on-light: #1E293B;
            --border-light: #E2E8F0;
            /* Brand */
            --accent: #0284C7;
            --accent-hover: #0369A1;
            --accent-light: rgba(2, 132, 199, 0.15);
            --brand-green: #10B981;
            --border: rgba(255, 255, 255, 0.06);
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
        }

        *, *::before, *::after { box-sizing: border-box; }

        body.app-layout {
            background-color: var(--bg-page);
            color: var(--text-main);
            font-family: var(--font-body);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .app-container {
            display: flex;
            flex: 1;
            width: 100%;
        }

        .main-content {
            flex: 1;
            padding: 32px 48px;
            background: var(--bg-page);
            min-height: calc(100vh - 60px);
        }
        
        .main-content.full-width {
            padding: 0;
        }

        /* Forms & Inputs */
        input.odl-input, select.odl-input {
            width: 100%;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 12px 16px;
            border-radius: 8px;
            font-family: var(--font-body);
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
            padding: 11px 22px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            font-family: var(--font-body);
            letter-spacing: -0.01em;
            cursor: pointer;
            transition: background 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }

        button.odl-btn-primary:hover {
            background: var(--accent-hover);
        }

        .success-text { color: var(--brand-green); font-size: 14px; }
        .error-text   { color: #EF4444; font-size: 14px; }
    """)
    
