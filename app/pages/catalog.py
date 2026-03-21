from fasthtml.common import *
from app.supabase_db import db_select

FREQ_COLOR = {
    "Real-time": "#10B981", "Streaming": "#10B981",
    "Hourly": "#3B82F6", "Daily": "#3B82F6",
    "Monthly": "#F59E0B", "Annual": "#94A3B8",
}
STATUS_BADGE = {
    "live": ("#10B981", "Live"),
    "coming_soon": ("#F59E0B", "Coming Soon"),
    "restricted": ("#EF4444", "Restricted"),
}

CATALOG_STYLE = Style("""
    .cat-layout { display: flex; gap: 32px; align-items: flex-start; }
    .cat-sidebar { width: 188px; flex-shrink: 0; }
    .cat-main { flex: 1; min-width: 0; }
    .cat-sidebar-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 7px 10px; border-radius: 6px; text-decoration: none;
        margin-bottom: 2px; transition: background 0.15s;
    }
    .cat-sidebar-item:hover { background: rgba(148,163,184,0.06); }
    .cat-sidebar-item.active { background: rgba(41,181,232,0.1); }
    .cat-sidebar-label { font-size: 13px; font-weight: 500; color: #CBD5E1; }
    .cat-sidebar-item.active .cat-sidebar-label { color: #29b5e8; }
    .cat-sidebar-count {
        font-size: 11px; color: #475569;
        background: rgba(148,163,184,0.08);
        padding: 1px 7px; border-radius: 999px;
    }
    .search-wrap { position: relative; margin-bottom: 24px; }
    .search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #475569; pointer-events: none; }
    .search-input {
        width: 100%; background: #0F1929;
        border: 1px solid rgba(148,163,184,0.15); color: #F8FAFC;
        padding: 10px 14px 10px 38px; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 14px; outline: none;
        transition: border-color 0.2s;
    }
    .search-input:focus { border-color: #29b5e8; }
    .search-input::placeholder { color: #334155; }
    .ds-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 16px; }
    .ds-card {
        display: flex; flex-direction: column; height: 100%;
        background: #0F1929; border: 1px solid rgba(148,163,184,0.1);
        border-radius: 10px; text-decoration: none;
        transition: border-color 0.2s, transform 0.15s;
    }
    .ds-card:hover { border-color: rgba(41,181,232,0.35); transform: translateY(-1px); }
    .ds-card-inner { display: flex; flex-direction: column; height: 100%; padding: 18px 20px; }
    .ds-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .ds-cat { font-size: 11px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; }
    .ds-title { font-size: 14px; font-weight: 600; color: #F8FAFC; line-height: 1.4; margin-bottom: 6px; }
    .ds-desc { font-size: 13px; color: #64748B; line-height: 1.55; flex: 1; margin-bottom: 14px; }
    .ds-footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid rgba(148,163,184,0.08); padding-top: 12px; }
    .ds-provider { font-size: 12px; color: #475569; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 55%; }
    .ds-badges { display: flex; gap: 5px; flex-shrink: 0; }
    .badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-api { background: rgba(41,181,232,0.12); color: #29b5e8; }
    .badge-sf { background: rgba(125,211,252,0.08); color: #7DD3FC; }
    .badge-status-live { color: #10B981; }
    .badge-status-coming { color: #F59E0B; }
""")


def _card(d):
    status_color, status_label = STATUS_BADGE.get(d.get("status", "live"), ("#64748B", "Unknown"))
    access = d.get("access_methods") or ["api"]
    return A(
        Div(
            Div(
                Span(d.get("category") or "", cls="ds-cat"),
                Span(status_label, style=f"font-size: 11px; font-weight: 600; color: {status_color};"),
                cls="ds-card-top"
            ),
            P(d.get("title") or "", cls="ds-title"),
            P(d.get("description") or "", cls="ds-desc"),
            Div(
                Span(d.get("provider") or "", cls="ds-provider"),
                Div(
                    *([Span("API", cls="badge badge-api")] if "api" in access else []),
                    *([Span("Snowflake", cls="badge badge-sf")] if "snowflake" in access else []),
                    cls="ds-badges"
                ),
                cls="ds-footer"
            ),
            cls="ds-card-inner"
        ),
        href=f"/catalog/{d['slug']}",
        cls="ds-card"
    )


def _sidebar(all_datasets, active_cat):
    counts = {}
    for d in all_datasets:
        c = d.get("category") or "Other"
        counts[c] = counts.get(c, 0) + 1
    total = len(all_datasets)
    items = [
        A(
            Span("All datasets", cls="cat-sidebar-label"),
            Span(str(total), cls="cat-sidebar-count"),
            href="/",
            cls=f"cat-sidebar-item {'active' if not active_cat else ''}",
        )
    ]
    for cat in sorted(counts):
        items.append(A(
            Span(cat, cls="cat-sidebar-label"),
            Span(str(counts[cat]), cls="cat-sidebar-count"),
            href=f"/?category={cat}",
            cls=f"cat-sidebar-item {'active' if cat == active_cat else ''}",
        ))
    return Div(*items, cls="cat-sidebar")


def DataCatalog(category: str = "", q: str = ""):
    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []

    datasets = all_datasets
    if q:
        ql = q.lower()
        datasets = [
            d for d in datasets
            if ql in (d.get("title") or "").lower()
            or ql in (d.get("description") or "").lower()
            or ql in " ".join(d.get("tags") or []).lower()
            or ql in (d.get("category") or "").lower()
            or ql in (d.get("provider") or "").lower()
        ]
    if category:
        datasets = [d for d in datasets if d.get("category") == category]

    heading_text = f'Results for "{q}"' if q else (category or "London Database")
    subtext = f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''} found" if (q or category) \
        else f"{len(datasets)} datasets — growing continuously"

    grid = Div(
        *[_card(d) for d in datasets],
        cls="ds-grid"
    ) if datasets else Div(
        P("No datasets match your search.", style="color: #64748B; font-size: 14px; padding: 32px 0 8px;"),
        A("Clear search", href="/", style="color: #29b5e8; font-size: 13px; text-decoration: none;"),
    )

    return Div(
        CATALOG_STYLE,
        # Search bar
        Div(
            Span(NotStr('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'), cls="search-icon"),
            Input(
                type="search", name="q", value=q,
                placeholder="Search by name, category, keyword, or provider…",
                cls="search-input",
                hx_get="/catalog/search",
                hx_trigger="input changed delay:280ms, search",
                hx_target="#catalog-body",
                hx_include="[name='q'],[name='category']",
            ),
            Input(type="hidden", name="category", value=category),
            cls="search-wrap"
        ),
        # Layout
        Div(
            _sidebar(all_datasets, category),
            Div(
                Div(
                    H1(heading_text, style="font-size: 19px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.3px;"),
                    P(subtext, style="font-size: 13px; color: #64748B; margin-top: 3px;"),
                    style="margin-bottom: 18px;"
                ),
                grid,
                id="catalog-body",
                cls="cat-main"
            ),
            cls="cat-layout"
        )
    )


def SearchCatalogResults(q: str = "", category: str = ""):
    return DataCatalog(q=q, category=category)
