from fasthtml.common import *
from app.supabase_db import db_select

STATUS_BADGE = {
    "live":        ("#10B981", "Live"),
    "coming_soon": ("#F59E0B", "Coming Soon"),
    "restricted":  ("#EF4444", "Restricted"),
}
FREQ_SHORT = {
    "Real-time": "Real-time", "Streaming": "Streaming",
    "Hourly": "Hourly", "Daily": "Daily", "Weekly": "Weekly",
    "Monthly": "Monthly", "Quarterly": "Quarterly", "Annual": "Annual",
    "Irregular": "Irregular", "One-off": "One-off",
}
CAT_COLORS = {
    "Corporate Registries":   "#6366F1",
    "Financial Regulation":   "#F59E0B",
    "Real Estate":            "#10B981",
    "Transportation":         "#3B82F6",
    "Public Safety":          "#EF4444",
    "Environment":            "#22C55E",
    "Demographics":           "#8B5CF6",
    "Health":                 "#EC4899",
    "Legal":                  "#F97316",
    "Education":              "#06B6D4",
    "Electoral":              "#A855F7",
}

CATALOG_STYLE = Style("""
    .cat-layout { display: flex; gap: 28px; align-items: flex-start; }
    .cat-sidebar { width: 200px; flex-shrink: 0; position: sticky; top: 20px; }
    .cat-main { flex: 1; min-width: 0; }

    .cat-sidebar-title { font-size: 11px; font-weight: 600; color: #475569;
        text-transform: uppercase; letter-spacing: 0.08em; padding: 0 10px; margin-bottom: 8px; }
    .cat-sidebar-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 6px 10px; border-radius: 6px; text-decoration: none;
        margin-bottom: 1px; transition: background 0.15s;
    }
    .cat-sidebar-item:hover { background: rgba(148,163,184,0.06); }
    .cat-sidebar-item.active { background: rgba(41,181,232,0.1); }
    .cat-sidebar-label { font-size: 13px; font-weight: 500; color: #94A3B8; }
    .cat-sidebar-item.active .cat-sidebar-label { color: #29b5e8; }
    .cat-sidebar-count { font-size: 11px; color: #475569;
        background: rgba(148,163,184,0.08); padding: 1px 6px; border-radius: 999px; }

    /* Search area */
    .search-area { margin-bottom: 20px; }
    .search-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
    .search-tab {
        padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
        cursor: pointer; border: 1px solid rgba(148,163,184,0.15);
        background: transparent; color: #64748B; transition: all 0.15s; font-family: 'Inter', sans-serif;
    }
    .search-tab.active { background: rgba(41,181,232,0.1); color: #29b5e8; border-color: rgba(41,181,232,0.25); }
    .search-tab:hover:not(.active) { background: rgba(148,163,184,0.06); color: #94A3B8; }

    .search-wrap { position: relative; }
    .search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
        color: #475569; pointer-events: none; }
    .search-input {
        width: 100%; background: #0F1929;
        border: 1px solid rgba(148,163,184,0.15); color: #F8FAFC;
        padding: 10px 14px 10px 38px; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 14px; outline: none;
        transition: border-color 0.2s;
    }
    .search-input:focus { border-color: #29b5e8; }
    .search-input::placeholder { color: #334155; }

    .ai-search-wrap { display: flex; gap: 10px; }
    .ai-input {
        flex: 1; background: #0F1929; border: 1px solid rgba(148,163,184,0.15);
        color: #F8FAFC; padding: 10px 14px; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 14px; outline: none;
        transition: border-color 0.2s; resize: none; min-height: 44px;
    }
    .ai-input:focus { border-color: #29b5e8; }
    .ai-input::placeholder { color: #334155; }
    .ai-btn {
        background: #29b5e8; color: #020617; font-weight: 700; font-size: 13px;
        padding: 0 20px; border: none; border-radius: 8px; cursor: pointer;
        font-family: 'Inter', sans-serif; white-space: nowrap; transition: opacity 0.2s;
        display: flex; align-items: center; gap: 8px;
    }
    .ai-btn:hover { opacity: 0.88; }
    .ai-btn[disabled] { opacity: 0.5; cursor: not-allowed; }
    .htmx-indicator { display: none; }
    .htmx-request .htmx-indicator { display: inline; }
    .htmx-request .ai-btn-label { display: none; }

    /* Dataset list */
    .ds-list { display: flex; flex-direction: column; }
    .ds-row {
        display: flex; align-items: center; gap: 14px;
        padding: 13px 16px; border-radius: 8px; text-decoration: none;
        transition: background 0.12s; border-bottom: 1px solid rgba(148,163,184,0.06);
    }
    .ds-row:last-child { border-bottom: none; }
    .ds-row:hover { background: rgba(148,163,184,0.05); }
    .ds-row-left { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
    .ds-row-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

    .ds-name { font-size: 14px; font-weight: 600; color: #F8FAFC;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ds-meta { display: flex; align-items: center; gap: 8px; }
    .ds-cat-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .ds-cat-label { font-size: 12px; color: #475569; }
    .ds-separator { color: #334155; font-size: 12px; }
    .ds-provider-label { font-size: 12px; color: #475569;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 260px; }
    .ds-desc { font-size: 13px; color: #64748B; line-height: 1.5;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .badge { padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-api { background: rgba(41,181,232,0.12); color: #29b5e8; }
    .badge-sf  { background: rgba(125,211,252,0.08); color: #7DD3FC; }
    .badge-freq { background: rgba(148,163,184,0.08); color: #64748B; font-weight: 500; }

    .status-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

    /* AI results */
    .ai-result-row {
        display: flex; gap: 14px; padding: 14px 16px;
        border-radius: 8px; text-decoration: none;
        border-bottom: 1px solid rgba(148,163,184,0.06);
        transition: background 0.12s;
    }
    .ai-result-row:last-child { border-bottom: none; }
    .ai-result-row:hover { background: rgba(148,163,184,0.05); }
    .ai-result-left { flex: 1; min-width: 0; }
    .ai-result-reason {
        font-size: 12px; color: #29b5e8; margin-top: 4px;
        line-height: 1.5; background: rgba(41,181,232,0.06);
        border-left: 2px solid rgba(41,181,232,0.3);
        padding: 4px 10px; border-radius: 0 4px 4px 0;
    }
    .ai-summary {
        background: rgba(41,181,232,0.06); border: 1px solid rgba(41,181,232,0.15);
        border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;
        font-size: 13px; color: #94A3B8; line-height: 1.6;
    }
    .ai-summary strong { color: #29b5e8; }

    .ds-list-wrap { background: #0F1929; border: 1px solid rgba(148,163,184,0.1); border-radius: 10px; overflow: hidden; }
    .ds-count-row { padding: 10px 16px; border-bottom: 1px solid rgba(148,163,184,0.08);
        font-size: 12px; color: #475569; display: flex; align-items: center; justify-content: space-between; }
""")


def _cat_color(cat):
    return CAT_COLORS.get(cat, "#64748B")


def _list_row(d, reason=None):
    status_color, status_label = STATUS_BADGE.get(d.get("status", "live"), ("#64748B", "Unknown"))
    access = d.get("access_methods") or ["api"]
    cat = d.get("category") or ""
    freq = FREQ_SHORT.get(d.get("update_frequency") or "", d.get("update_frequency") or "")

    name_and_meta = Div(
        Div(d.get("title") or "", cls="ds-name"),
        Div(
            Div(style=f"width:6px;height:6px;border-radius:50%;background:{_cat_color(cat)};flex-shrink:0;"),
            Span(cat, cls="ds-cat-label"),
            Span("·", cls="ds-separator"),
            Span(d.get("provider") or "", cls="ds-provider-label"),
            cls="ds-meta"
        ),
        Span(d.get("description") or "", cls="ds-desc"),
        cls="ds-row-left"
    )
    right = Div(
        *([Span(freq, cls="badge badge-freq")] if freq else []),
        *([Span("API", cls="badge badge-api")] if "api" in access else []),
        *([Span("Snowflake", cls="badge badge-sf")] if "snowflake" in access else []),
        Div(title=status_label, style=f"width:7px;height:7px;border-radius:50%;background:{status_color};"),
        cls="ds-row-right"
    )

    if reason:
        return A(
            Div(name_and_meta, right, style="display:flex;align-items:center;gap:14px;"),
            P(reason, cls="ai-result-reason"),
            href=f"/catalog/{d['slug']}",
            cls="ai-result-row"
        )

    return A(name_and_meta, right, href=f"/catalog/{d['slug']}", cls="ds-row")


def _sidebar(all_datasets, active_cat):
    counts = {}
    for d in all_datasets:
        c = d.get("category") or "Other"
        counts[c] = counts.get(c, 0) + 1
    total = len(all_datasets)

    items = [
        Div("Categories", cls="cat-sidebar-title"),
        A(
            Span("All datasets", cls="cat-sidebar-label"),
            Span(str(total), cls="cat-sidebar-count"),
            href="/catalog",
            cls=f"cat-sidebar-item {'active' if not active_cat else ''}",
        )
    ]
    for cat in sorted(counts):
        items.append(A(
            Span(cat, cls="cat-sidebar-label"),
            Span(str(counts[cat]), cls="cat-sidebar-count"),
            href=f"/catalog?category={cat}",
            cls=f"cat-sidebar-item {'active' if cat == active_cat else ''}",
        ))
    return Div(*items, cls="cat-sidebar")


def _search_area(q, category):
    keyword_panel = Div(
        Div(
            NotStr('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'),
            cls="search-icon"
        ),
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
    )

    ai_panel = Div(
        Form(
            Div(
                Input(
                    type="text", name="query",
                    placeholder="Describe what you're looking for, e.g. 'company director information for KYC' or 'property prices in London over time'…",
                    cls="ai-input",
                ),
                Button(
                    Span("Ask AI", cls="ai-btn-label"),
                    NotStr('<span class="htmx-indicator">Searching…</span>'),
                    type="submit",
                    cls="ai-btn",
                ),
                cls="ai-search-wrap"
            ),
            hx_post="/catalog/ai-search",
            hx_target="#catalog-body",
            hx_indicator=".ai-btn",
        ),
        id="ai-panel", style="display:none;"
    )

    return Div(
        Div(
            Button("Keyword search", cls="search-tab active",
                   onclick="setTab('keyword', this)"),
            Button("✦ AI search", cls="search-tab",
                   onclick="setTab('ai', this)"),
            cls="search-tabs"
        ),
        keyword_panel,
        ai_panel,
        Script("""
            function setTab(tab, btn) {
                document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('keyword-panel') && (document.getElementById('keyword-panel').style.display = tab === 'keyword' ? '' : 'none');
                document.getElementById('ai-panel').style.display = tab === 'ai' ? '' : 'none';
                // wrap keyword in id if needed
                var kw = document.querySelector('.search-wrap');
                if (kw) kw.style.display = tab === 'keyword' ? '' : 'none';
            }
        """),
        cls="search-area"
    )


def _dataset_list(datasets, heading, subtext):
    if not datasets:
        return Div(
            P("No datasets match your search.", style="color:#64748B;font-size:14px;padding:32px 0 8px;"),
            A("Clear search", href="/catalog", style="color:#29b5e8;font-size:13px;text-decoration:none;"),
        )
    return Div(
        Div(
            H1(heading, style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;"),
            P(subtext, style="font-size:13px;color:#64748B;margin-top:3px;"),
            style="margin-bottom:16px;"
        ),
        Div(
            Div(f"{len(datasets)} datasets", cls="ds-count-row"),
            Div(*[_list_row(d) for d in datasets], cls="ds-list"),
            cls="ds-list-wrap"
        )
    )


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

    heading = f'Results for "{q}"' if q else (category or "London Database")
    subtext = (f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''} found"
               if (q or category) else f"{len(datasets)} datasets — growing continuously")

    return Div(
        CATALOG_STYLE,
        _search_area(q, category),
        Div(
            _sidebar(all_datasets, category),
            Div(
                _dataset_list(datasets, heading, subtext),
                id="catalog-body",
                cls="cat-main"
            ),
            cls="cat-layout"
        )
    )


def SearchCatalogResults(q: str = "", category: str = ""):
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

    heading = f'Results for "{q}"' if q else (category or "London Database")
    subtext = (f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''} found"
               if (q or category) else f"{len(datasets)} datasets — growing continuously")
    return _dataset_list(datasets, heading, subtext)


def AiSearchResults(query: str):
    """Call Claude with the catalog and user's natural language query."""
    import os, json
    try:
        import anthropic
    except ImportError:
        return Div("AI search is not available — anthropic package not installed.", style="color:#EF4444;font-size:13px;padding:20px 0;")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return Div("AI search is not configured.", style="color:#EF4444;font-size:13px;padding:20px 0;")

    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []

    # Build compact catalog for the prompt
    catalog_lines = []
    for d in all_datasets:
        tags = ", ".join(d.get("tags") or [])
        catalog_lines.append(
            f'slug:{d["slug"]} | title:{d.get("title","")} | category:{d.get("category","")} '
            f'| description:{d.get("description","")} | tags:{tags}'
        )
    catalog_text = "\n".join(catalog_lines)

    prompt = f"""You are a data catalog assistant. A user is looking for datasets that match their use case.
Below is a catalog of available datasets. Return a JSON array of the most relevant datasets for the user's query.

USER QUERY: {query}

CATALOG:
{catalog_text}

Respond with ONLY a JSON array (no markdown, no explanation outside the JSON). Each item must have:
- "slug": the dataset slug
- "reason": one sentence explaining specifically why this dataset is relevant to the user's query

Return between 3 and 10 results, ranked by relevance. Only include datasets that are genuinely useful for the query. If nothing matches well, return an empty array []."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        matches = json.loads(raw.strip())
    except Exception as e:
        return Div(f"AI search failed: {str(e)}", style="color:#EF4444;font-size:13px;padding:20px 0;")

    if not matches:
        return Div(
            Div(f'No datasets found for: "{query}"', cls="ai-summary"),
            P("Try rephrasing your query or browse the catalog by category.", style="color:#64748B;font-size:13px;"),
        )

    # Look up full dataset records
    slug_to_reason = {m["slug"]: m.get("reason", "") for m in matches}
    slug_order = [m["slug"] for m in matches]
    ds_map = {d["slug"]: d for d in all_datasets}
    ordered = [ds_map[s] for s in slug_order if s in ds_map]

    return Div(
        Div(
            NotStr(f'<strong>{len(ordered)} datasets</strong> matched your query: "<em>{query}</em>"'),
            cls="ai-summary"
        ),
        Div(
            Div(f"{len(ordered)} AI-matched datasets", cls="ds-count-row"),
            Div(*[_list_row(d, reason=slug_to_reason.get(d["slug"], "")) for d in ordered], cls="ds-list"),
            cls="ds-list-wrap"
        )
    )
