"""
Explore module page — data access options, grouped by persona.
"""
from fasthtml.common import *

EXPLORE_STYLE = Style("""
    .explore-wrap {
        max-width: 1120px;
        margin: 0 auto;
        padding: 32px 24px 56px;
    }

    /* ── Hero ─────────────────────────────────────────────── */
    .explore-hero {
        margin-bottom: 32px;
    }
    .explore-title {
        font-family: var(--font-display);
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--text-main);
        margin: 0 0 8px;
    }
    .explore-subtitle {
        margin: 0;
        max-width: 720px;
        color: var(--text-muted);
        font-size: 15px;
        line-height: 1.65;
    }

    /* ── Persona filter pills ─────────────────────────────── */
    .persona-filters {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 28px;
    }
    .persona-pill {
        padding: 7px 16px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: var(--bg-surface);
        color: var(--text-muted);
        font-family: var(--font-body);
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s;
        white-space: nowrap;
    }
    .persona-pill:hover {
        color: var(--text-main);
        border-color: var(--text-muted);
        background: var(--bg-muted);
    }
    .persona-pill.active {
        color: #FFFFFF;
        background: var(--accent);
        border-color: var(--accent);
        font-weight: 600;
        box-shadow: var(--shadow);
    }

    /* ── Section groups ───────────────────────────────────── */
    .explore-section {
        margin-bottom: 32px;
    }
    .explore-section.hidden {
        display: none;
    }
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }
    .section-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
    }
    .section-title {
        font-family: var(--font-display);
        font-size: 18px;
        font-weight: 600;
        color: var(--text-main);
        margin: 0;
        letter-spacing: -0.01em;
    }
    .section-desc {
        font-size: 13px;
        color: var(--text-faint);
        margin: 0;
    }

    /* ── Card grid ────────────────────────────────────────── */
    .explore-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 12px;
    }

    .explore-card {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 18px 18px 16px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        transition: border-color 0.2s, background 0.2s, transform 0.15s;
        position: relative;
        text-decoration: none;
    }
    .explore-card:hover {
        border-color: var(--accent);
        background: var(--bg-muted);
        transform: translateY(-1px);
    }
    .explore-card.coming-soon {
        opacity: 0.55;
        pointer-events: none;
    }

    .card-top-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .card-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    .card-title-block {
        flex: 1;
        min-width: 0;
    }
    .explore-card-title {
        margin: 0;
        color: var(--text-main);
        font-size: 15px;
        font-weight: 600;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    .card-status {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        font-weight: 600;
        margin-top: 3px;
    }
    .card-status.live {
        color: var(--brand-green);
    }
    .card-status.coming-soon {
        color: #F59E0B;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
    }
    .status-dot.live {
        background: var(--brand-green);
    }
    .status-dot.coming-soon {
        background: #F59E0B;
    }

    .explore-card-desc {
        margin: 0;
        color: var(--text-muted);
        font-size: 13px;
        line-height: 1.55;
        flex: 1;
    }

    .card-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        margin-top: auto;
        padding-top: 4px;
    }
    .explore-tag-row {
        display: flex;
        gap: 5px;
        flex-wrap: wrap;
    }
    .explore-tag {
        font-size: 11px;
        border-radius: 999px;
        border: 1px solid var(--border);
        color: var(--text-muted);
        padding: 2px 8px;
        background: var(--bg-surface);
    }
    .card-arrow {
        color: var(--text-faint);
        font-size: 16px;
        flex-shrink: 0;
        transition: color 0.15s, transform 0.15s;
    }
    .explore-card:hover .card-arrow {
        color: var(--accent);
        transform: translateX(2px);
    }

    /* ── Responsive ───────────────────────────────────────── */
    @media (max-width: 700px) {
        .explore-grid {
            grid-template-columns: 1fr;
        }
        .explore-title {
            font-size: 24px;
        }
    }
""")


SECTION_ICON_COLORS = {
    "query":    "background: var(--accent-light); color: var(--accent);",
    "connect":  "background: rgba(16,185,129,0.15); color: #34D399;",
    "share":    "background: rgba(236,72,153,0.15); color: #F472B6;",
    "automate": "background: rgba(245,158,11,0.15); color: #FBBF24;",
}

CARD_ICON_STYLES = {
    "sql":        "background: var(--accent-light); color: var(--accent);",
    "ai":         "background: rgba(139,92,246,0.12); color: #A78BFA;",
    "graphql":    "background: rgba(236,72,153,0.12); color: #F472B6;",
    "rest":       "background: rgba(59,130,246,0.12); color: #60A5FA;",
    "snowflake":  "background: rgba(56,189,248,0.12); color: #38BDF8;",
    "mcp":        "background: rgba(16,185,129,0.12); color: #34D399;",
    "download":   "background: var(--bg-muted); color: var(--text-muted);",
    "bi":         "background: rgba(245,158,11,0.12); color: #FBBF24;",
    "sheet":      "background: rgba(34,197,94,0.12);  color: #4ADE80;",
    "report":     "background: rgba(249,115,22,0.12); color: #FB923C;",
}


ACCESS_SECTIONS = [
    {
        "id": "query",
        "icon": "&#xf121;",
        "title": "Query & Analyse",
        "desc": "Write queries or ask questions to explore data directly.",
        "cards": [
            {
                "key": "sql",
                "icon": "&gt;_",
                "title": "SQL Query Workspace",
                "desc": "Write and run SQL in the browser for ad-hoc analysis, joins, and validation.",
                "tags": ["Developers", "Analysts"],
                "status": "live",
                "href": "/queries",
            },
            {
                "key": "ai",
                "icon": "&#x2728;",
                "title": "AI Data Assistant",
                "desc": "Ask questions in plain language. Get relevant tables, suggested queries, and insights.",
                "tags": ["Non-technical", "Analysts"],
                "status": "coming_soon",
                "href": None,
            },
        ],
    },
    {
        "id": "connect",
        "icon": "&#x1F50C;",
        "title": "Connect & Integrate",
        "desc": "Consume data directly in your apps, pipelines, or warehouse.",
        "cards": [
            {
                "key": "rest",
                "icon": "{ }",
                "title": "REST API",
                "desc": "HTTP endpoints for automation, custom apps, and backend service integration.",
                "tags": ["Developers", "Automation"],
                "status": "live",
                "href": "/integrations",
            },
            {
                "key": "graphql",
                "icon": "&#x25C8;",
                "title": "Graph API",
                "desc": "Structured graph-based queries for relationship-rich datasets and linked data.",
                "tags": ["Developers", "Applications"],
                "status": "coming_soon",
                "href": None,
            },
            {
                "key": "snowflake",
                "icon": "&#x2744;",
                "title": "Snowflake Secure Share",
                "desc": "Access curated datasets in your Snowflake warehouse — no file copying required.",
                "tags": ["Data teams", "Enterprise"],
                "status": "coming_soon",
                "href": None,
            },
            {
                "key": "mcp",
                "icon": "&#x2699;",
                "title": "MCP Server",
                "desc": "Connect data to AI agents and tools via the Model Context Protocol.",
                "tags": ["Developers", "AI workflows"],
                "status": "coming_soon",
                "href": None,
            },
        ],
    },
    {
        "id": "share",
        "icon": "&#x1F4E4;",
        "title": "Export & Share",
        "desc": "Download data or open it in familiar tools for quick sharing.",
        "cards": [
            {
                "key": "download",
                "icon": "&#x21E9;",
                "title": "Export to File",
                "desc": "Download filtered results as CSV or JSON for local analysis and offline sharing.",
                "tags": ["Everyone", "Portable"],
                "status": "live",
                "href": "/catalog",
            },
            {
                "key": "sheet",
                "icon": "&#x25A6;",
                "title": "Spreadsheet Access",
                "desc": "Open data in Excel or Google Sheets for lightweight analysis and familiar workflows.",
                "tags": ["Non-technical", "Ops teams"],
                "status": "coming_soon",
                "href": None,
            },
        ],
    },
    {
        "id": "automate",
        "icon": "&#x1F504;",
        "title": "Report & Automate",
        "desc": "Schedule deliveries and plug into dashboards for ongoing reporting.",
        "cards": [
            {
                "key": "bi",
                "icon": "&#x1F4CA;",
                "title": "BI Connectors",
                "desc": "Plug into Power BI, Tableau, or Looker for dashboards and stakeholder reporting.",
                "tags": ["Analysts", "Business users"],
                "status": "coming_soon",
                "href": None,
            },
            {
                "key": "report",
                "icon": "&#x1F4E8;",
                "title": "Scheduled Reports",
                "desc": "Deliver recurring data snapshots to teams by email on a schedule you define.",
                "tags": ["Business users", "Operations"],
                "status": "coming_soon",
                "href": None,
            },
        ],
    },
]


def _collect_personas():
    """Gather unique persona tags across all cards for the filter bar."""
    seen = []
    for section in ACCESS_SECTIONS:
        for card in section["cards"]:
            for tag in card["tags"]:
                if tag not in seen:
                    seen.append(tag)
    return seen


def _access_card(card):
    is_live = card["status"] == "live"
    status_label = "Available" if is_live else "Coming Soon"
    status_cls = "live" if is_live else "coming-soon"
    icon_style = CARD_ICON_STYLES.get(card["key"], "background:rgba(255,255,255,0.08);color:#94A3B8;")

    tag_attr = " ".join(card["tags"])

    inner = Div(
        Div(
            Div(NotStr(card["icon"]), cls="card-icon", style=icon_style),
            Div(
                H3(card["title"], cls="explore-card-title"),
                Div(
                    Span(cls=f"status-dot {status_cls}"),
                    Span(status_label),
                    cls=f"card-status {status_cls}"
                ),
                cls="card-title-block"
            ),
            cls="card-top-row"
        ),
        P(card["desc"], cls="explore-card-desc"),
        Div(
            Div(*[Span(t, cls="explore-tag") for t in card["tags"]], cls="explore-tag-row"),
            *([Span(NotStr("&#x2192;"), cls="card-arrow")] if is_live else []),
            cls="card-footer"
        ),
        data_personas=tag_attr,
    )

    if is_live and card.get("href"):
        return A(
            inner,
            href=card["href"],
            cls="explore-card",
            style="text-decoration:none;",
            data_personas=tag_attr,
        )

    return Div(
        inner,
        cls=f"explore-card {'coming-soon' if not is_live else ''}",
        data_personas=tag_attr,
    )


def _section(section_data):
    icon_style = SECTION_ICON_COLORS.get(section_data["id"], "background:rgba(255,255,255,0.08);color:#94A3B8;")
    return Div(
        Div(
            Div(NotStr(section_data["icon"]), cls="section-icon", style=icon_style),
            Div(
                H2(section_data["title"], cls="section-title"),
                P(section_data["desc"], cls="section-desc"),
            ),
            cls="section-header"
        ),
        Div(
            *[_access_card(c) for c in section_data["cards"]],
            cls="explore-grid"
        ),
        cls="explore-section",
        data_section=section_data["id"],
    )


def ExploreChat():
    """Data access options grouped by use-case, filterable by persona."""
    personas = _collect_personas()

    filter_script = Script("""
        (function() {
            const pills = document.querySelectorAll('.persona-pill');
            const cards = document.querySelectorAll('[data-personas]');
            const sections = document.querySelectorAll('.explore-section');
            let active = 'all';

            function applyFilter(persona) {
                active = persona;
                pills.forEach(p => p.classList.toggle('active', p.dataset.persona === persona));

                if (persona === 'all') {
                    cards.forEach(c => c.style.display = '');
                    sections.forEach(s => s.classList.remove('hidden'));
                    return;
                }

                cards.forEach(c => {
                    const ps = (c.getAttribute('data-personas') || '').split(' ');
                    c.style.display = ps.includes(persona) ? '' : 'none';
                });

                sections.forEach(s => {
                    const visibleCards = s.querySelectorAll('.explore-card:not([style*="display: none"])');
                    s.classList.toggle('hidden', visibleCards.length === 0);
                });
            }

            pills.forEach(p => {
                p.addEventListener('click', () => applyFilter(p.dataset.persona));
            });
        })();
    """)

    return Div(
        EXPLORE_STYLE,
        Div(
            H1("Choose How You Access Data", cls="explore-title"),
            P(
                "Pick the access path that fits your workflow — from no-code reporting "
                "and spreadsheets to APIs, SQL, and AI-native integrations.",
                cls="explore-subtitle"
            ),
            cls="explore-hero"
        ),
        Div(
            Button("All", cls="persona-pill active", data_persona="all"),
            *[Button(p, cls="persona-pill", data_persona=p) for p in personas],
            cls="persona-filters"
        ),
        *[_section(s) for s in ACCESS_SECTIONS],
        filter_script,
        cls="explore-wrap"
    )
