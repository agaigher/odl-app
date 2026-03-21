from fasthtml.common import Style

def get_shared_style():
    """
    Global dark theme, inspired by Financial Datasets.

    - Near-black canvas background
    - High-contrast white headings and muted body copy
    - Minimal accent color, white CTAs
    """
    return Style("""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Roboto+Mono:wght@400;700&display=swap');
        
        :root {
            /* Core palette */
            --odl-bg: #f8f9fa;
            --odl-bg-elevated: #ffffff;
            --odl-border-subtle: rgba(0, 0, 0, 0.1);
            --odl-text: #111827;
            --odl-text-muted: #4b5563;
            --odl-accent: #f97316; /* soft orange accent */
            --odl-accent-soft: rgba(249, 115, 22, 0.15);
            
            --odl-font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        
        /* Global Reset */
        * {
            box-sizing: border-box;
        }

        body {
            background-color: var(--odl-bg) !important;
            background-image: url('data:image/svg+xml,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noiseFilter"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/%3E%3C/filter%3E%3Crect width="100%25" height="100%25" filter="url(%23noiseFilter)" opacity="0.05"/%3E%3C/svg%3E');
            color: var(--odl-text) !important;
            font-family: var(--odl-font-family) !important;
            margin: 0;
            -webkit-font-smoothing: antialiased;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--odl-font-family) !important;
            font-weight: 700;
            color: var(--odl-text);
            margin-top: 0;
        }

        /* Core layout container */
        .odl-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 32px;
        }
        
        @media (min-width: 1280px) {
            .odl-container {
                max-width: 1200px;
                padding: 0;
            }
        }
        
        /* Generic dark section */
        .odl-section {
            background-color: transparent;
            padding: 56px 0;
        }
        
        /* Global links: subtle, no bright GOV.UK blue */
        a {
            color: var(--odl-text);
            text-decoration: none;
            transition: opacity 0.15s ease, color 0.15s ease, background-color 0.15s ease;
        }
        
        a:hover {
            opacity: 0.8;
        }
        
        /* Generic CTA buttons */
        .odl-btn-primary {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 9px 20px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background-color: #f3f4f6; /* softer off-white, like FD */
            color: #111827;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
        }
        
        .odl-btn-primary:hover {
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.6);
            background-color: #e5e7eb;
        }
        
        .odl-btn-secondary {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 9px 20px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.22);
            background-color: transparent;
            color: var(--odl-text);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
        }
        
        .odl-btn-secondary:hover {
            background-color: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 255, 255, 0.5);
        }
    """)


def get_content_page_style():
    """
    Dark-theme content layout for inner pages (same look as home).
    Apply body class 'odl-page' to use. Use with get_shared_style().
    """
    return Style("""
        body.odl-page .content-wrapper {
            max-width: 800px;
            margin: 0 auto;
            padding: 60px 40px;
        }

        body.odl-page .page-title {
            font-size: 48px;
            font-weight: 700;
            color: var(--odl-text);
            margin-bottom: 20px;
            line-height: 1.2;
            letter-spacing: -1px;
        }

        body.odl-page .page-subtitle {
            font-size: 18px;
            color: var(--odl-text-muted);
            margin-bottom: 50px;
            font-weight: 400;
        }

        body.odl-page .content-section {
            margin-bottom: 60px;
        }

        body.odl-page .section-title {
            font-size: 24px;
            font-weight: 600;
            color: var(--odl-text);
            margin-bottom: 16px;
            font-family: var(--odl-font-family);
        }

        body.odl-page .section-description,
        body.odl-page .section-text {
            font-size: 16px;
            color: var(--odl-text-muted);
            line-height: 1.8;
            margin-bottom: 20px;
        }

        body.odl-page a {
            color: var(--odl-text);
            text-decoration: none;
            transition: opacity 0.2s;
        }

        body.odl-page a:hover {
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            body.odl-page .content-wrapper {
                padding: 40px 20px;
            }
            body.odl-page .page-title {
                font-size: 36px;
            }
        }
    """)
