"""
All CSS styles for the ODL application.

- get_app_style()          – dark app shell (authenticated pages)
- get_shared_style()       – light marketing / content pages
- get_content_page_style() – inner content layout for light pages
"""
from fasthtml.common import Style


def get_app_style():
    return Style("""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap');

        :root {
            --font-display: "Space Grotesk", system-ui, sans-serif;
            --font-body: "Inter", system-ui, sans-serif;
            --font-mono: "JetBrains Mono", ui-monospace, monospace;
            --bg-page: #080a0f;
            --bg-elevated: #0f1118;
            --bg-surface: #141824;
            --bg-card: #161a2a;
            --bg-muted: #0c1018;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --text-faint: #475569;
            --surface-light: #FFFFFF;
            --text-on-light: #1E293B;
            --border-light: #E2E8F0;
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
            margin: 0; padding: 0;
            display: flex; flex-direction: column;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .app-container { display: flex; flex: 1; width: 100%; }

        .main-content {
            flex: 1; padding: 32px 48px;
            background: var(--bg-page);
            min-height: calc(100vh - 60px);
        }
        .main-content.full-width { padding: 0; }

        input.odl-input, select.odl-input {
            width: 100%; background: var(--bg-surface);
            border: 1px solid var(--border); color: var(--text-main);
            padding: 12px 16px; border-radius: 8px;
            font-family: var(--font-body); font-size: 14px; margin-bottom: 16px;
        }
        input.odl-input:focus, select.odl-input:focus {
            outline: none; border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(2,132,199,0.12);
        }

        button.odl-btn-primary {
            background: var(--accent); color: #ffffff; border: none;
            padding: 11px 22px; border-radius: 8px; font-weight: 500;
            font-size: 14px; font-family: var(--font-body);
            letter-spacing: -0.01em; cursor: pointer;
            transition: background 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }
        button.odl-btn-primary:hover { background: var(--accent-hover); }

        .success-text { color: var(--brand-green); font-size: 14px; }
        .error-text   { color: #EF4444; font-size: 14px; }
    """)


def get_shared_style():
    return Style("""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Roboto+Mono:wght@400;700&display=swap');
        :root {
            --odl-bg: #f7f7f4; --odl-bg-elevated: #ffffff;
            --odl-border-subtle: rgba(0, 0, 0, 0.1);
            --odl-text: #111827; --odl-text-muted: #4b5563;
            --odl-accent: #f97316; --odl-accent-soft: rgba(249, 115, 22, 0.15);
            --odl-font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        * { box-sizing: border-box; }
        body {
            background-color: var(--odl-bg) !important;
            color: var(--odl-text) !important;
            font-family: var(--odl-font-family) !important;
            margin: 0; -webkit-font-smoothing: antialiased;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--odl-font-family) !important; font-weight: 700;
            color: var(--odl-text); margin-top: 0;
        }
        .odl-container { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 32px; }
        @media (min-width: 1280px) { .odl-container { max-width: 1200px; padding: 0; } }
        .odl-section { background-color: transparent; padding: 56px 0; }
        a { color: var(--odl-text); text-decoration: none; transition: opacity 0.15s ease, color 0.15s ease, background-color 0.15s ease; }
        a:hover { opacity: 0.8; }
        .odl-btn-primary {
            display: inline-flex; align-items: center; justify-content: center;
            padding: 9px 20px; border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background-color: #f3f4f6; color: #111827;
            font-size: 14px; font-weight: 600; cursor: pointer;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
        }
        .odl-btn-primary:hover { box-shadow: 0 10px 26px rgba(0, 0, 0, 0.6); background-color: #e5e7eb; }
        .odl-btn-secondary {
            display: inline-flex; align-items: center; justify-content: center;
            padding: 9px 20px; border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.22);
            background-color: transparent; color: var(--odl-text);
            font-size: 14px; font-weight: 500; cursor: pointer;
        }
        .odl-btn-secondary:hover { background-color: rgba(255, 255, 255, 0.06); border-color: rgba(255, 255, 255, 0.5); }
    """)


def get_content_page_style():
    return Style("""
        body.odl-page .content-wrapper { max-width: 800px; margin: 0 auto; padding: 60px 40px; }
        body.odl-page .page-title { font-size: 48px; font-weight: 700; color: var(--odl-text); margin-bottom: 20px; line-height: 1.2; letter-spacing: -1px; }
        body.odl-page .page-subtitle { font-size: 18px; color: var(--odl-text-muted); margin-bottom: 50px; font-weight: 400; }
        body.odl-page .content-section { margin-bottom: 60px; }
        body.odl-page .section-title { font-size: 24px; font-weight: 600; color: var(--odl-text); margin-bottom: 16px; font-family: var(--odl-font-family); }
        body.odl-page .section-description, body.odl-page .section-text { font-size: 16px; color: var(--odl-text-muted); line-height: 1.8; margin-bottom: 20px; }
        body.odl-page a { color: var(--odl-text); text-decoration: none; transition: opacity 0.2s; }
        body.odl-page a:hover { opacity: 0.8; }
        @media (max-width: 768px) {
            body.odl-page .content-wrapper { padding: 40px 20px; }
            body.odl-page .page-title { font-size: 36px; }
        }
    """)
