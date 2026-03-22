from fasthtml.common import *
from app.supabase_db import db_select

STATUS_BADGE = {
    "live":        ("#10B981", "Live"),
    "coming_soon": ("#F59E0B", "Coming Soon"),
    "restricted":  ("#EF4444", "Restricted"),
}
FREQ_SHORT = {
    "Real-time": "Real-time", "Streaming": "Real-time",
    "Hourly": "Hourly", "Daily": "Daily", "Weekly": "Weekly",
    "Monthly": "Monthly", "Quarterly": "Quarterly", "Annual": "Annual",
    "Irregular": "Irregular", "One-off": "One-off",
}
CAT_COLORS = {
    "Corporate Registries": "#6366F1",
    "Financial Regulation": "#F59E0B",
    "Real Estate":          "#10B981",
    "Transportation":       "#3B82F6",
    "Public Safety":        "#EF4444",
    "Environment":          "#22C55E",
    "Demographics":         "#8B5CF6",
    "Health":               "#EC4899",
    "Legal":                "#F97316",
    "Education":            "#06B6D4",
    "Electoral":            "#A855F7",
}
ACCESS_FILTERS  = [("All",       ""),           ("API",       "api"),  ("Snowflake", "snowflake")]
FREQ_FILTERS    = [("All",       ""),           ("Real-time", "Real-time"), ("Daily", "Daily"),
                   ("Monthly",   "Monthly"),    ("Annual",    "Annual")]

CATALOG_STYLE = Style("""
    .cat-wrap { display: flex; gap: 28px; align-items: flex-start; }
    .cat-sidebar { width: 200px; flex-shrink: 0; position: sticky; top: 20px; }
    .cat-main { flex: 1; min-width: 0; }

    /* Sidebar */
    .cat-sidebar-title { font-size: 11px; font-weight: 600; color: #475569;
        text-transform: uppercase; letter-spacing: 0.08em; padding: 0 10px; margin-bottom: 8px; }
    .cat-sidebar-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 6px 10px; border-radius: 6px; text-decoration: none;
        margin-bottom: 1px; transition: background 0.15s; gap: 6px;
    }
    .cat-sidebar-item:hover { background: rgba(148,163,184,0.06); }
    .cat-sidebar-item.active { background: rgba(41,181,232,0.1); }
    .cat-sidebar-label { font-size: 13px; font-weight: 500; color: #94A3B8; flex: 1; }
    .cat-sidebar-item.active .cat-sidebar-label { color: #29b5e8; }
    .cat-sidebar-count { font-size: 11px; color: #475569;
        background: rgba(148,163,184,0.08); padding: 1px 6px; border-radius: 999px; flex-shrink: 0; }

    /* Search tabs */
    .search-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
    .stab { padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
        cursor: pointer; border: 1px solid rgba(148,163,184,0.15);
        background: transparent; color: #64748B; font-family: 'Inter', sans-serif;
        transition: all 0.15s; }
    .stab.on { background: rgba(41,181,232,0.1); color: #29b5e8; border-color: rgba(41,181,232,0.25); }
    .stab:hover:not(.on) { color: #94A3B8; background: rgba(148,163,184,0.06); }

    /* Keyword search */
    .kw-wrap { position: relative; margin-bottom: 0; }
    .kw-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
        color: #475569; pointer-events: none; }
    .kw-input { width: 100%; background: #0F1929;
        border: 1px solid rgba(148,163,184,0.15); color: #F8FAFC;
        padding: 10px 14px 10px 38px; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 14px; outline: none; transition: border-color 0.2s; }
    .kw-input:focus { border-color: #29b5e8; }
    .kw-input::placeholder { color: #334155; }

    /* AI search */
    .ai-wrap { display: flex; gap: 10px; }
    .ai-input { flex: 1; background: #0F1929; border: 1px solid rgba(148,163,184,0.15);
        color: #F8FAFC; padding: 10px 14px; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 14px; outline: none; transition: border-color 0.2s; }
    .ai-input:focus { border-color: #29b5e8; }
    .ai-input::placeholder { color: #334155; }
    .ai-btn { background: #29b5e8; color: #020617; font-weight: 700; font-size: 13px;
        padding: 0 20px; border: none; border-radius: 8px; cursor: pointer;
        font-family: 'Inter', sans-serif; white-space: nowrap; transition: opacity 0.2s; height: 42px; }
    .ai-btn:hover { opacity: 0.88; }
    .ai-form.htmx-request .ai-btn { opacity: 0.5; cursor: not-allowed; }
    .ai-form.htmx-request .ai-btn::after { content: "…"; }

    /* Filter chips */
    .filters { display: flex; align-items: center; gap: 16px; margin: 14px 0; flex-wrap: wrap; }
    .filter-group { display: flex; align-items: center; gap: 6px; }
    .filter-label { font-size: 11px; font-weight: 600; color: #475569;
        text-transform: uppercase; letter-spacing: 0.06em; }
    .chip { padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 500;
        text-decoration: none; color: #64748B; border: 1px solid rgba(148,163,184,0.12);
        background: transparent; cursor: pointer; transition: all 0.12s; white-space: nowrap; }
    .chip:hover { color: #94A3B8; border-color: rgba(148,163,184,0.25); }
    .chip.on { background: rgba(41,181,232,0.1); color: #29b5e8; border-color: rgba(41,181,232,0.3); }

    /* Dataset list */
    .ds-list-box { background: #0F1929; border: 1px solid rgba(148,163,184,0.1);
        border-radius: 10px; overflow: hidden; }
    .ds-count-bar { padding: 9px 16px; border-bottom: 1px solid rgba(148,163,184,0.08);
        font-size: 12px; color: #475569; display: flex; align-items: center; justify-content: space-between; }
    .ds-list { display: flex; flex-direction: column; }
    .ds-row { display: flex; align-items: center; gap: 10px; padding: 11px 14px;
        border-bottom: 1px solid rgba(148,163,184,0.05); transition: background 0.1s; }
    .ds-row:last-child { border-bottom: none; }
    .ds-row:hover { background: rgba(148,163,184,0.04); }

    .ds-row-mid { flex: 1; min-width: 0; }
    .ds-name { font-size: 14px; font-weight: 600; color: #F8FAFC; text-decoration: none;
        display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; }
    .ds-name:hover { color: #29b5e8; }
    .ds-meta { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
    .ds-cat-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .ds-cat-label { font-size: 12px; color: #475569; }
    .ds-sep { color: #334155; font-size: 12px; }
    .ds-prov { font-size: 12px; color: #475569; white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis; max-width: 220px; }
    .ds-desc { font-size: 12px; color: #475569; margin-top: 2px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .ds-row-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
    .badge { padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-api  { background: rgba(41,181,232,0.12); color: #29b5e8; }
    .badge-sf   { background: rgba(125,211,252,0.08); color: #7DD3FC; }
    .badge-freq { background: rgba(148,163,184,0.08); color: #64748B; font-weight: 500; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

    /* Star (favourite) button */
    .fav-btn { background: transparent; border: none; cursor: pointer;
        font-size: 16px; color: #334155; padding: 2px 4px; line-height: 1;
        transition: color 0.15s; flex-shrink: 0; }
    .fav-btn:hover { color: #F59E0B; }
    .fav-btn.on { color: #F59E0B; }

    /* Add button */
    .add-btn { background: transparent; border: 1px solid rgba(148,163,184,0.2);
        color: #94A3B8; font-size: 12px; font-weight: 600; padding: 3px 10px;
        border-radius: 5px; cursor: pointer; font-family: 'Inter', sans-serif;
        transition: all 0.15s; white-space: nowrap; flex-shrink: 0; }
    .add-btn:hover { border-color: #29b5e8; color: #29b5e8; }
    .added-badge { font-size: 12px; font-weight: 600; color: #10B981;
        padding: 3px 10px; white-space: nowrap; }

    /* AI results */
    .ai-reason { font-size: 12px; color: #64748B; margin-top: 3px;
        padding-left: 4px; border-left: 2px solid rgba(41,181,232,0.3);
        padding-left: 8px; line-height: 1.5; }
    .ai-banner { background: rgba(41,181,232,0.06); border: 1px solid rgba(41,181,232,0.15);
        border-radius: 8px; padding: 10px 14px; margin-bottom: 14px;
        font-size: 13px; color: #64748B; }
    .ai-banner strong { color: #29b5e8; }

    .empty-msg { padding: 40px 20px; color: #475569; font-size: 14px; text-align: center; }
""")


# ── Small reusable components ─────────────────────────────────────────────────

def _fav_btn(slug, is_fav):
    return Button(
        "★" if is_fav else "☆",
        hx_post=f"/catalog/{slug}/favourite",
        hx_target=f"#fav-{slug}",
        hx_swap="outerHTML",
        id=f"fav-{slug}",
        cls=f"fav-btn {'on' if is_fav else ''}",
        title="Remove from favourites" if is_fav else "Add to favourites",
    )


def _add_btn(slug, is_added):
    if is_added:
        return Div(
            Span("✓ Added", cls="added-badge"),
            Button("Remove",
                hx_post=f"/catalog/{slug}/remove",
                hx_target=f"#add-{slug}",
                hx_swap="outerHTML",
                style="background:transparent;border:none;color:#475569;font-size:11px;cursor:pointer;padding:0 4px;font-family:'Inter',sans-serif;",
            ),
            id=f"add-{slug}",
            style="display:flex;align-items:center;gap:4px;",
        )
    return Button(
        "+ Add",
        hx_post=f"/catalog/{slug}/add",
        hx_target=f"#add-{slug}",
        hx_swap="outerHTML",
        id=f"add-{slug}",
        cls="add-btn",
        title="Add this dataset to your account",
    )


def _list_row(d, is_added=False, is_fav=False, ai_reason=None):
    slug = d.get("slug", "")
    status_color, status_label = STATUS_BADGE.get(d.get("status", "live"), ("#64748B", "Unknown"))
    access = d.get("access_methods") or ["api"]
    cat   = d.get("category") or ""
    freq  = FREQ_SHORT.get(d.get("update_frequency") or "", "")
    color = CAT_COLORS.get(cat, "#64748B")

    mid = Div(
        A(d.get("title") or slug, href=f"/catalog/{slug}", cls="ds-name"),
        Div(
            Div(style=f"width:6px;height:6px;border-radius:50%;background:{color};flex-shrink:0;"),
            Span(cat, cls="ds-cat-label"),
            Span("·", cls="ds-sep"),
            Span(d.get("provider") or "", cls="ds-prov"),
            cls="ds-meta"
        ),
        *([ P(ai_reason, cls="ai-reason") ] if ai_reason else
          [ Span(d.get("description") or "", cls="ds-desc") ]),
        cls="ds-row-mid"
    )
    right = Div(
        *([Span(freq, cls="badge badge-freq")] if freq else []),
        *([Span("API", cls="badge badge-api")] if "api" in access else []),
        *([Span("Snowflake", cls="badge badge-sf")] if "snowflake" in access else []),
        Div(title=status_label, style=f"width:7px;height:7px;border-radius:50%;background:{status_color};"),
        _add_btn(slug, is_added),
        cls="ds-row-right"
    )
    return Div(_fav_btn(slug, is_fav), mid, right, cls="ds-row")


# ── Filter chips ──────────────────────────────────────────────────────────────

def _chip(label, param, value, current, category, q, access_f, freq_f):
    is_on = (current == value) or (value == "" and not current)
    # Build full query string for this chip's state
    a = value if param == "access" else access_f
    f = value if param == "freq"   else freq_f
    qs = f"q={q}&category={category}&access={a}&freq={f}"
    return A(
        label,
        hx_get=f"/catalog/search?{qs}",
        hx_target="#catalog-body",
        hx_push_url=f"/catalog?{qs}",
        cls=f"chip {'on' if is_on else ''}",
    )


def _filter_chips(access_f, freq_f, category, q):
    access_chips = [
        _chip(label, "access", val, access_f, category, q, access_f, freq_f)
        for label, val in ACCESS_FILTERS
    ]
    freq_chips = [
        _chip(label, "freq", val, freq_f, category, q, access_f, freq_f)
        for label, val in FREQ_FILTERS
    ]
    return Div(
        Div(Span("Access", cls="filter-label"), *access_chips, cls="filter-group"),
        Div(Span("Frequency", cls="filter-label"), *freq_chips, cls="filter-group"),
        cls="filters"
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar(all_datasets, active_cat):
    counts = {}
    for d in all_datasets:
        c = d.get("category") or "Other"
        counts[c] = counts.get(c, 0) + 1
    total = len(all_datasets)

    items = [
        Div("Browse", cls="cat-sidebar-title"),
        A(
            Span("All datasets", cls="cat-sidebar-label"),
            Span(str(total), cls="cat-sidebar-count"),
            href="/catalog",
            cls=f"cat-sidebar-item {'active' if not active_cat else ''}",
        ),
        A(
            Span("Favourites", cls="cat-sidebar-label"),
            href="/favourites",
            cls="cat-sidebar-item",
            style="margin-top:4px;"
        ),
        Div("Categories", cls="cat-sidebar-title", style="margin-top:20px;"),
    ]
    for cat in sorted(counts):
        items.append(A(
            Span(cat, cls="cat-sidebar-label"),
            Span(str(counts[cat]), cls="cat-sidebar-count"),
            href=f"/catalog?category={cat}",
            cls=f"cat-sidebar-item {'active' if cat == active_cat else ''}",
        ))
    return Div(*items, cls="cat-sidebar")


# ── Search area ───────────────────────────────────────────────────────────────

def _search_area(q, category, access_f, freq_f):
    return Div(
        Div(
            Button("Keyword search", id="tab-kw", cls="stab on",
                   onclick="showTab('kw')"),
            Button("✦ AI search", id="tab-ai", cls="stab",
                   onclick="showTab('ai')"),
            cls="search-tabs"
        ),
        # Keyword panel
        Div(
            Div(
                NotStr('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'),
                cls="kw-icon"
            ),
            Input(type="search", name="q", value=q,
                  placeholder="Search by name, category, keyword, or provider…",
                  cls="kw-input",
                  hx_get="/catalog/search",
                  hx_trigger="input changed delay:280ms, search",
                  hx_target="#catalog-body",
                  hx_include="[name='q'],[name='category'],[name='access'],[name='freq']",
                  hx_push_url="true"),
            Input(type="hidden", name="category", value=category),
            Input(type="hidden", name="access",   value=access_f),
            Input(type="hidden", name="freq",     value=freq_f),
            cls="kw-wrap"
        ),
        # AI panel (hidden initially)
        Form(
            Div(
                Input(type="text", name="query",
                      placeholder="Describe what you need, e.g. 'company director data for KYC' or 'property prices in London over time'…",
                      cls="ai-input"),
                Button("Ask AI", type="submit", cls="ai-btn"),
                cls="ai-wrap"
            ),
            hx_post="/catalog/ai-search",
            hx_target="#catalog-body",
            cls="ai-form",
            style="display:none;",
            id="panel-ai"
        ),
        Script("""
            function showTab(tab) {
                document.getElementById('tab-kw').classList.toggle('on', tab === 'kw');
                document.getElementById('tab-ai').classList.toggle('on', tab === 'ai');
                document.querySelector('.kw-wrap').style.display = tab === 'kw' ? '' : 'none';
                document.getElementById('panel-ai').style.display  = tab === 'ai' ? '' : 'none';
            }
        """),
        style="margin-bottom: 4px;"
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_user_sets(user_id):
    """Return (added_slugs set, fav_slugs set) for a given user_id."""
    added, favs = set(), set()
    if not user_id:
        return added, favs
    try:
        for row in db_select("dataset_access", {"user_id": user_id}):
            if row.get("status") != "removed":
                added.add(row["dataset_slug"])
    except Exception:
        pass
    try:
        for row in db_select("favourites", {"user_id": user_id}):
            favs.add(row["dataset_slug"])
    except Exception:
        pass
    return added, favs


def _apply_filters(datasets, q, category, access_f, freq_f):
    if q:
        ql = q.lower()
        datasets = [d for d in datasets
                    if ql in (d.get("title") or "").lower()
                    or ql in (d.get("description") or "").lower()
                    or ql in " ".join(d.get("tags") or []).lower()
                    or ql in (d.get("category") or "").lower()
                    or ql in (d.get("provider") or "").lower()]
    if category:
        datasets = [d for d in datasets if d.get("category") == category]
    if access_f:
        datasets = [d for d in datasets if access_f in (d.get("access_methods") or [])]
    if freq_f:
        datasets = [d for d in datasets
                    if FREQ_SHORT.get(d.get("update_frequency") or "", "") == freq_f
                    or d.get("update_frequency") == freq_f]
    return datasets


def _list_body(datasets, added, favs, heading, subtext):
    if not datasets:
        return Div(
            Div(
                H1(heading, style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;"),
                P(subtext, style="font-size:13px;color:#64748B;margin-top:3px;"),
                style="margin-bottom:14px;"
            ),
            Div(P("No datasets match.", cls="empty-msg"), cls="ds-list-box"),
        )
    return Div(
        Div(
            H1(heading, style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;"),
            P(subtext, style="font-size:13px;color:#64748B;margin-top:3px;"),
            style="margin-bottom:14px;"
        ),
        Div(
            Div(f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''}", cls="ds-count-bar"),
            Div(*[_list_row(d,
                            is_added=d.get("slug") in added,
                            is_fav=d.get("slug") in favs)
                  for d in datasets], cls="ds-list"),
            cls="ds-list-box"
        )
    )


# ── Public components ─────────────────────────────────────────────────────────

def DataCatalog(category="", q="", user_id="", access_filter="", freq_filter=""):
    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []

    added, favs = _fetch_user_sets(user_id)
    datasets    = _apply_filters(all_datasets, q, category, access_filter, freq_filter)

    heading = f'Results for "{q}"' if q else (category or "London Database")
    subtext = (f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''} found"
               if (q or category or access_filter or freq_filter)
               else f"{len(datasets)} datasets — growing continuously")

    return Div(
        CATALOG_STYLE,
        _search_area(q, category, access_filter, freq_filter),
        _filter_chips(access_filter, freq_filter, category, q),
        Div(
            _sidebar(all_datasets, category),
            Div(
                _list_body(datasets, added, favs, heading, subtext),
                id="catalog-body",
                cls="cat-main"
            ),
            cls="cat-wrap"
        )
    )


def SearchCatalogResults(q="", category="", user_id="", access_filter="", freq_filter=""):
    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []

    added, favs = _fetch_user_sets(user_id)
    datasets    = _apply_filters(all_datasets, q, category, access_filter, freq_filter)

    heading = f'Results for "{q}"' if q else (category or "London Database")
    subtext = (f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''} found"
               if (q or category or access_filter or freq_filter)
               else f"{len(datasets)} datasets — growing continuously")

    return _list_body(datasets, added, favs, heading, subtext)


def FavouritesView(user_id=""):
    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []

    added, favs = _fetch_user_sets(user_id)
    ds_map = {d["slug"]: d for d in all_datasets}
    datasets = [ds_map[s] for s in favs if s in ds_map]

    if not datasets:
        return Div(
            CATALOG_STYLE,
            Div(
                H1("Favourites", style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;margin-bottom:8px;"),
                P("Star a dataset from the catalog to save it here.", style="font-size:14px;color:#64748B;margin-bottom:20px;"),
                A("Browse the catalog →", href="/catalog", style="color:#29b5e8;font-size:14px;text-decoration:none;"),
            )
        )

    return Div(
        CATALOG_STYLE,
        Div(
            Div(
                H1("Favourites", style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;"),
                P(f"{len(datasets)} starred dataset{'s' if len(datasets) != 1 else ''}", style="font-size:13px;color:#64748B;margin-top:3px;"),
                style="margin-bottom:14px;"
            ),
            Div(
                Div(f"{len(datasets)} favourites", cls="ds-count-bar"),
                Div(*[_list_row(d, is_added=d.get("slug") in added, is_fav=True)
                      for d in datasets], cls="ds-list"),
                cls="ds-list-box"
            )
        )
    )


def AiSearchResults(query="", user_id=""):
    import os, json
    if not query.strip():
        return Div(P("Please enter a query.", style="color:#64748B;font-size:13px;padding:20px 0;"))
    try:
        import anthropic
    except ImportError:
        return Div(P("AI search unavailable — anthropic package not installed.", style="color:#EF4444;font-size:13px;padding:20px 0;"))

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return Div(P("AI search is not configured (missing API key).", style="color:#EF4444;font-size:13px;padding:20px 0;"))

    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []

    added, favs = _fetch_user_sets(user_id)

    catalog_lines = []
    for d in all_datasets:
        tags = ", ".join(d.get("tags") or [])
        catalog_lines.append(
            f'slug:{d["slug"]} | title:{d.get("title","")} | category:{d.get("category","")} '
            f'| description:{d.get("description","")} | tags:{tags}'
        )

    prompt = f"""You are a data catalog assistant. A user is looking for datasets.

USER QUERY: {query}

CATALOG:
{chr(10).join(catalog_lines)}

Return ONLY a JSON array of the 3-10 most relevant datasets. Each item:
{{"slug": "...", "reason": "one sentence why this is relevant to the user query"}}

Rank by relevance. If nothing matches, return []."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        matches = json.loads(raw.strip())
    except Exception as e:
        return Div(P(f"AI search error: {e}", style="color:#EF4444;font-size:13px;padding:20px 0;"))

    if not matches:
        return Div(
            P(f'No datasets matched: "{query}"', cls="ai-banner"),
            P("Try rephrasing or browse by category.", style="color:#64748B;font-size:13px;"),
        )

    slug_to_reason = {m["slug"]: m.get("reason", "") for m in matches}
    ds_map  = {d["slug"]: d for d in all_datasets}
    ordered = [ds_map[s] for s in [m["slug"] for m in matches] if s in ds_map]

    return Div(
        Div(
            NotStr(f'<strong>{len(ordered)} datasets</strong> matched: "<em>{query}</em>"'),
            cls="ai-banner"
        ),
        Div(
            Div(f"{len(ordered)} AI-matched datasets", cls="ds-count-bar"),
            Div(*[_list_row(d,
                            is_added=d.get("slug") in added,
                            is_fav=d.get("slug") in favs,
                            ai_reason=slug_to_reason.get(d.get("slug"), ""))
                  for d in ordered], cls="ds-list"),
            cls="ds-list-box"
        )
    )
