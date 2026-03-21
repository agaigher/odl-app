from fasthtml.common import *
from app.components import odl_navbar, odl_sidebar

def get_app_style():
    # Base application styling (extends odl-web's styles)
    return Style("""
        :root {
            --bg-dark: #020617;
            --bg-card: #0F172A;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --accent: #29b5e8;
            --border: rgba(148, 163, 184, 0.15);
        }
        
        body.app-layout {
            background-color: var(--bg-dark);
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
            /* Below navbar height roughly */
            height: calc(100vh - 65px); 
            overflow: hidden;
        }

        .main-content {
            flex: 1;
            padding: 32px 48px;
            overflow-y: auto;
            background: var(--bg-dark);
        }

        /* Forms & Inputs */
        input.odl-input, select.odl-input {
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 12px 16px;
            border-radius: 8px;
            font-family: 'Roboto Mono', monospace;
            font-size: 14px;
            margin-bottom: 16px;
        }

        input.odl-input:focus, select.odl-input:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 1px var(--accent);
        }

        button.odl-btn-primary {
            background: var(--accent);
            color: #0b0c0c;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }

        button.odl-btn-primary:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
    """)
    
