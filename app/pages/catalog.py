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
ACCESS_FILTERS = [("All", ""), ("API", "api"), ("Snowflake", "snowflake")]
FREQ_FILTERS   = [("All", ""), ("Real-time", "Real-time"), ("Daily", "Daily"),
                  ("Monthly", "Monthly"), ("Annual", "Annual")]

CATALOG_STYLE = Style("""
    .cat-wrap { display: flex; gap: 24px; align-items: flex-start; }
    .cat-sidebar { width: 190px; flex-shrink: 0; position: sticky; top: 20px; }
    .cat-main { flex: 1; min-width: 0; }

    .cat-sidebar-title { font-size: 10px; font-weight: 700; color: #94A3B8;
        text-transform: uppercase; letter-spacing: 0.1em; padding: 0 8px; margin-bottom: 6px; }
    .cat-sidebar-item { display: flex; align-items: center; justify-content: space-between;
        padding: 6px 8px; border-radius: 6px; text-decoration: none;
        margin-bottom: 1px; transition: background 0.12s; gap: 6px; }
    .cat-sidebar-item:hover { background: #F1F5F9; }
    .cat-sidebar-item.active { background: #E0F2FE; }
    .cat-sidebar-label { font-size: 13px; font-weight: 500; color: #475569; flex: 1; }
    .cat-sidebar-item.active .cat-sidebar-label { color: #0284C7; font-weight: 600; }
    .cat-sidebar-count { font-size: 11px; color: #94A3B8;
        background: #F1F5F9; padding: 1px 6px; border-radius: 999px; }

    .search-tabs { display: flex; gap: 4px; margin-bottom: 10px; }
    .stab { padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
        cursor: pointer; border: 1px solid #E2E8F0;
        background: #FFFFFF; color: #64748B; font-family: 'Inter', sans-serif;
        transition: all 0.15s; }
    .stab.on { background: #E0F2FE; color: #0284C7; border-color: #BAE6FD; font-weight: 600; }
    .stab:hover:not(.on) { background: #F8FAFC; color: #374151; }

    .kw-wrap { position: relative; }
    .kw-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
        color: #94A3B8; pointer-events: none; }
    .kw-input { width: 100%; background: #FFFFFF;
        border: 1px solid #E2E8F0; color: #1E293B;
        padding: 10px 14px 10px 38px; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 14px; outline: none; transition: border-color 0.2s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .kw-input:focus { border-color: #0284C7; box-shadow: 0 0 0 3px rgba(2,132,199,0.1); }
    .kw-input::placeholder { color: #CBD5E1; }

    .ai-wrap { display: flex; gap: 10px; }
    .ai-input { flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0;
        color: #1E293B; padding: 10px 14px; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 14px; outline: none; transition: border-color 0.2s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .ai-input:focus { border-color: #0284C7; box-shadow: 0 0 0 3px rgba(2,132,199,0.1); }
    .ai-input::placeholder { color: #CBD5E1; }
    .ai-btn { background: #0284C7; color: #ffffff; font-weight: 700; font-size: 13px;
        padding: 0 20px; border: none; border-radius: 8px; cursor: pointer;
        font-family: 'Inter', sans-serif; white-space: nowrap; height: 42px;
        transition: background 0.15s; }
    .ai-btn:hover { background: #0369A1; }
    .ai-form.htmx-request .ai-btn { opacity: 0.6; cursor: not-allowed; }
    .ai-form.htmx-request .ai-btn::after { content: "…"; }

    .filters { display: flex; align-items: center; gap: 16px; margin: 12px 0; flex-wrap: wrap; }
    .filter-group { display: flex; align-items: center; gap: 5px; }
    .filter-label { font-size: 11px; font-weight: 700; color: #94A3B8;
        text-transform: uppercase; letter-spacing: 0.06em; }
    .chip { padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 500;
        text-decoration: none; color: #64748B; border: 1px solid #E2E8F0;
        background: #FFFFFF; cursor: pointer; transition: all 0.12s; white-space: nowrap; }
    .chip:hover { color: #1E293B; border-color: #CBD5E1; background: #F8FAFC; }
    .chip.on { background: #E0F2FE; color: #0284C7; border-color: #BAE6FD; font-weight: 600; }

    .ds-list-box { background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 10px; overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .ds-count-bar { padding: 8px 16px; border-bottom: 1px solid #F1F5F9;
        font-size: 12px; color: #94A3B8; background: #FAFAFA; }
    .ds-list { display: flex; flex-direction: column; }
    .ds-row { display: flex; align-items: center; gap: 10px; padding: 11px 14px;
        border-bottom: 1px solid #F8FAFC; transition: background 0.1s; }
    .ds-row:last-child { border-bottom: none; }
    .ds-row:hover { background: #F8FAFC; }

    .ds-row-mid { flex: 1; min-width: 0; }
    .ds-name { font-size: 14px; font-weight: 600; color: #1E293B; text-decoration: none;
        display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; }
    .ds-name:hover { color: #0284C7; }
    .ds-meta { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
    .ds-cat-label { font-size: 12px; color: #94A3B8; }
    .ds-sep { color: #CBD5E1; font-size: 12px; }
    .ds-prov { font-size: 12px; color: #94A3B8; white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis; max-width: 220px; }
    .ds-desc { font-size: 12px; color: #94A3B8; margin-top: 2px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .ds-row-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
    .badge { padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-api  { background: #E0F2FE; color: #0284C7; }
    .badge-sf   { background: #EFF6FF; color: #3B82F6; }
    .badge-freq { background: #F1F5F9; color: #64748B; font-weight: 500; }

    .fav-btn { background: transparent; border: none; cursor: pointer;
        font-size: 20px; color: #CBD5E1; padding: 3px 6px; line-height: 1;
        transition: color 0.15s; flex-shrink: 0; }
    .fav-btn:hover { color: #F59E0B; }
    .fav-btn.on { color: #F59E0B; }

    .add-btn { background: #FFFFFF; border: 1px solid #E2E8F0;
        color: #64748B; font-size: 12px; font-weight: 600; padding: 4px 11px;
        border-radius: 5px; cursor: pointer; font-family: 'Inter', sans-serif;
        transition: all 0.15s; white-space: nowrap; flex-shrink: 0; }
    .add-btn:hover { border-color: #0284C7; color: #0284C7; background: #E0F2FE; }
    .added-badge { font-size: 12px; font-weight: 600; color: #16A34A; padding: 3px 6px;
        white-space: nowrap; }
    .remove-link { background: transparent; border: none; color: #CBD5E1; font-size: 11px;
        cursor: pointer; padding: 0; font-family: 'Inter', sans-serif; }
    .remove-link:hover { color: #EF4444; }

    .ai-reason { font-size: 12px; color: #64748B; margin-top: 3px;
        border-left: 2px solid #BAE6FD; padding-left: 8px; line-height: 1.5; }
    .ai-banner { background: #F0F9FF; border: 1px solid #BAE6FD;
        border-radius: 8px; padding: 10px 14px; margin-bottom: 14px;
        font-size: 13px; color: #0369A1; }
    .empty-msg { padding: 40px 20px; color: #94A3B8; font-size: 14px; text-align: center; }

    .fav-section { margin-bottom: 32px; }
    .fav-section-title { font-size: 15px; font-weight: 600; color: #1E293B;
        margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .fav-section-count { font-size: 12px; color: #94A3B8; font-weight: 400; }
""")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _cat_color(cat):
    return CAT_COLORS.get(cat, "#64748B")


def _fetch_user_sets(user_id):
    """Return (added_slugs, fav_slugs) for a user. fav_slugs = in any list."""
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
        for row in db_select("favourite_items", {"user_id": user_id}):
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


# ── Row-level components ──────────────────────────────────────────────────────

def _fav_btn(slug, is_fav, oob=False):
    attrs = {"hx_swap_oob": "true"} if oob else {}
    return Button(
        "★" if is_fav else "☆",
        type="button",
        hx_get=f"/catalog/{slug}/favourite-modal",
        hx_target="#modal-root",
        hx_swap="innerHTML",
        hx_trigger="click",
        id=f"fav-{slug}",
        cls=f"fav-btn {'on' if is_fav else ''}",
        title="Save to a list",
        **attrs
    )


def _add_btn(slug, is_added):
    if is_added:
        return Div(
            Span("✓ Added", cls="added-badge"),
            Button("Remove",
                   hx_post=f"/catalog/{slug}/remove",
                   hx_target=f"#add-{slug}",
                   hx_swap="outerHTML",
                   cls="remove-link"),
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


def _list_checkbox(list_id, slug, in_list, list_name):
    """A single list row inside the favourite modal — toggleable via HTMX."""
    return Div(
        Input(
            type="checkbox",
            checked=in_list,
            hx_post=f"/favourite-lists/{list_id}/toggle?slug={slug}",
            hx_trigger="change",
            hx_target=f"#lcheck-{list_id}",
            hx_swap="outerHTML",
            hx_include="this",
        ),
        Span(list_name, cls="list-check-name"),
        id=f"lcheck-{list_id}",
        cls="list-check-row",
    )


def _list_row(d, is_added=False, is_fav=False, ai_reason=None):
    slug   = d.get("slug", "")
    status_color, status_label = STATUS_BADGE.get(d.get("status", "live"), ("#64748B", "Unknown"))
    access = d.get("access_methods") or ["api"]
    cat    = d.get("category") or ""
    freq   = FREQ_SHORT.get(d.get("update_frequency") or "", "")
    color  = _cat_color(cat)

    mid = Div(
        A(d.get("title") or slug, href=f"/catalog/{slug}", cls="ds-name"),
        Div(
            Div(style=f"width:6px;height:6px;border-radius:50%;background:{color};flex-shrink:0;"),
            Span(cat, cls="ds-cat-label"),
            Span("·", cls="ds-sep"),
            Span(d.get("provider") or "", cls="ds-prov"),
            cls="ds-meta"
        ),
        *([P(ai_reason, cls="ai-reason")] if ai_reason else
          [Span(d.get("description") or "", cls="ds-desc")]),
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


# ── Favourite modal ───────────────────────────────────────────────────────────

def FavouriteModal(slug, dataset_title, user_id):
    try:
        lists = db_select("favourite_lists", {"user_id": user_id})
    except Exception:
        lists = []

    try:
        items = db_select("favourite_items", {"user_id": user_id, "dataset_slug": slug})
    except Exception:
        items = []

    in_list_ids = {item["list_id"] for item in items}

    list_rows = [
        _list_checkbox(lst["id"], slug, lst["id"] in in_list_ids, lst["name"])
        for lst in lists
    ]

    empty_msg = P("No lists yet. Create one below.", cls="modal-empty") if not lists else None

    new_list_form = Form(
        Div(
            Input(type="hidden", name="slug", value=slug),
            Input(type="text", name="name", placeholder="New list name…",
                  required=True, cls="modal-new-input"),
            Button("Create", type="submit", cls="modal-create-btn"),
            cls="modal-new-list"
        ),
        hx_post="/favourite-lists",
        hx_target="#modal-lists",
        hx_swap="beforeend",
        hx_on__after_request="this.reset()",
    )

    close_and_update = Script(f"""
        document.getElementById('modal-done').addEventListener('click', function() {{
            htmx.ajax('GET', '/catalog/{slug}/fav-btn', '#fav-{slug}');
            document.getElementById('modal-root').innerHTML = '';
        }});
    """)

    return Div(
        Div(style="position:absolute;inset:0;",
            onclick="document.getElementById('modal-root').innerHTML=''"),
        Div(
            P("★ Save to a list", cls="modal-title"),
            P(dataset_title, cls="modal-sub"),
            Hr(cls="modal-divider"),
            Div(empty_msg, *list_rows, id="modal-lists"),
            Hr(cls="modal-divider"),
            new_list_form,
            Hr(cls="modal-divider"),
            Button("Done", id="modal-done", cls="modal-done-btn"),
            close_and_update,
            cls="modal-box"
        ),
        cls="modal-backdrop"
    )


# ── Filter chips ──────────────────────────────────────────────────────────────

def _chip(label, param, value, current, category, q, access_f, freq_f):
    is_on = (current == value) or (value == "" and not current)
    a = value if param == "access" else access_f
    f = value if param == "freq"   else freq_f
    qs = f"q={q}&category={category}&access={a}&freq={f}"
    return A(label,
             hx_get=f"/catalog/search?{qs}",
             hx_target="#catalog-body",
             hx_push_url=f"/catalog?{qs}",
             cls=f"chip {'on' if is_on else ''}")


def _filter_chips(access_f, freq_f, category, q):
    return Div(
        Div(Span("Access", cls="filter-label"),
            *[_chip(l, "access", v, access_f, category, q, access_f, freq_f) for l, v in ACCESS_FILTERS],
            cls="filter-group"),
        Div(Span("Frequency", cls="filter-label"),
            *[_chip(l, "freq", v, freq_f, category, q, access_f, freq_f) for l, v in FREQ_FILTERS],
            cls="filter-group"),
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
        A(Span("All datasets", cls="cat-sidebar-label"),
          Span(str(total), cls="cat-sidebar-count"),
          href="/catalog",
          cls=f"cat-sidebar-item {'active' if not active_cat else ''}"),
        A(Span("Favourites", cls="cat-sidebar-label"),
          href="/favourites",
          cls="cat-sidebar-item",
          style="margin-top:4px;"),
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
            Button("Keyword search", id="tab-kw", cls="stab on", onclick="showTab('kw')"),
            Button("✦ AI search",    id="tab-ai", cls="stab",    onclick="showTab('ai')"),
            cls="search-tabs"
        ),
        Div(
            Div(NotStr('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'),
                cls="kw-icon"),
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
            id="panel-kw", cls="kw-wrap"
        ),
        Form(
            Div(
                Input(type="text", name="query",
                      placeholder="Describe what you need, e.g. 'company director data for KYC'…",
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
                document.getElementById('tab-kw').classList.toggle('on', tab==='kw');
                document.getElementById('tab-ai').classList.toggle('on', tab==='ai');
                document.getElementById('panel-kw').style.display = tab==='kw' ? '' : 'none';
                document.getElementById('panel-ai').style.display = tab==='ai' ? '' : 'none';
            }
        """),
        style="margin-bottom:4px;"
    )


# ── List body ─────────────────────────────────────────────────────────────────

def _list_body(datasets, added, favs, heading, subtext):
    if not datasets:
        return Div(
            Div(H1(heading, style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;"),
                P(subtext, style="font-size:13px;color:#64748B;margin-top:3px;"),
                style="margin-bottom:14px;"),
            Div(P("No datasets match.", cls="empty-msg"), cls="ds-list-box"),
        )
    return Div(
        Div(H1(heading, style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;"),
            P(subtext, style="font-size:13px;color:#64748B;margin-top:3px;"),
            style="margin-bottom:14px;"),
        Div(
            Div(f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''}", cls="ds-count-bar"),
            Div(*[_list_row(d, is_added=d.get("slug") in added, is_fav=d.get("slug") in favs)
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
            Div(_list_body(datasets, added, favs, heading, subtext),
                id="catalog-body", cls="cat-main"),
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
        lists = db_select("favourite_lists", {"user_id": user_id})
    except Exception:
        lists = []

    if not lists:
        return Div(
            CATALOG_STYLE,
            H1("Favourites", style="font-size:18px;font-weight:700;color:#F8FAFC;margin-bottom:8px;"),
            P("You haven't saved anything yet.", style="font-size:14px;color:#64748B;margin-bottom:16px;"),
            P("Click the ☆ star on any dataset to save it to a list.",
              style="font-size:13px;color:#475569;margin-bottom:20px;"),
            A("Browse the catalog →", href="/catalog", style="color:#29b5e8;font-size:14px;text-decoration:none;"),
        )

    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []
    ds_map = {d["slug"]: d for d in all_datasets}

    added, _ = _fetch_user_sets(user_id)

    sections = []
    for lst in lists:
        try:
            items = db_select("favourite_items", {"list_id": lst["id"]})
        except Exception:
            items = []
        slugs = [item["dataset_slug"] for item in items]
        datasets = [ds_map[s] for s in slugs if s in ds_map]
        if not datasets:
            continue
        sections.append(Div(
            P(lst["name"],
              Span(f"{len(datasets)} dataset{'s' if len(datasets)!=1 else ''}",
                   cls="fav-section-count"),
              cls="fav-section-title"),
            Div(
                Div(f"{len(datasets)} dataset{'s' if len(datasets)!=1 else ''}", cls="ds-count-bar"),
                Div(*[_list_row(d, is_added=d.get("slug") in added, is_fav=True)
                      for d in datasets], cls="ds-list"),
                cls="ds-list-box"
            ),
            cls="fav-section"
        ))

    return Div(
        CATALOG_STYLE,
        H1("Favourites", style="font-size:18px;font-weight:700;color:#F8FAFC;letter-spacing:-0.3px;margin-bottom:24px;"),
        *sections if sections else [P("Your lists are empty.", style="color:#475569;font-size:14px;")]
    )


def AiSearchResults(query="", user_id=""):
    import os, json
    if not query.strip():
        return Div(P("Please enter a query.", style="color:#64748B;font-size:13px;padding:20px 0;"))
    try:
        import anthropic
    except ImportError:
        return Div(P("AI search unavailable — anthropic package not installed.",
                     style="color:#EF4444;font-size:13px;padding:20px 0;"))

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return Div(P("AI search is not configured.", style="color:#EF4444;font-size:13px;padding:20px 0;"))

    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []

    added, favs = _fetch_user_sets(user_id)

    catalog_lines = [
        f'slug:{d["slug"]} | title:{d.get("title","")} | category:{d.get("category","")} '
        f'| description:{d.get("description","")} | tags:{", ".join(d.get("tags") or [])}'
        for d in all_datasets
    ]

    prompt = f"""You are a data catalog assistant. A user is looking for datasets.

USER QUERY: {query}

CATALOG:
{chr(10).join(catalog_lines)}

Return ONLY a JSON array of the 3-10 most relevant datasets. Each item:
{{"slug": "...", "reason": "one sentence why this matches the user query"}}

Rank by relevance. If nothing matches well, return []."""

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
        Div(NotStr(f'<strong>{len(ordered)} datasets</strong> matched: "<em>{query}</em>"'),
            cls="ai-banner"),
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
