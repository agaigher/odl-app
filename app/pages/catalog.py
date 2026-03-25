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
    /* Dark surfaces — aligned with dashboard (no stark white on #080a0f) */
    .cat-wrap { display: flex; width: 100%; min-height: calc(100vh - 60px); align-items: flex-start; }
    .cat-sidebar {
        width: 240px; flex-shrink: 0;
        position: sticky;
        top: 60px;
        height: calc(100vh - 60px);
        overflow-y: auto;
        -ms-overflow-style: none;
        scrollbar-width: none;
        padding: 40px 16px 24px;
        border-right: 1px solid rgba(255,255,255,0.05);
        background: #14120b;
    }
    .cat-sidebar::-webkit-scrollbar { width: 0; height: 0; display: none; }
    .cat-main-col { flex: 1; min-width: 0; padding: 32px 48px; }
    .cat-main { min-width: 0; }
    .cat-content-grid { display: grid; grid-template-columns: minmax(280px, 1fr) minmax(0, 2fr); gap: 20px; align-items: start; }
    .cat-controls-col { min-width: 0; }
    .cat-results-col { min-width: 0; }

    .cat-sidebar-title {
        font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700;
        color: #475569; text-transform: uppercase; letter-spacing: 0.1em;
        padding-left: 4px; margin-bottom: 12px;
    }
    .cat-sidebar-item {
        display: flex; align-items: center; justify-content: space-between; gap: 8px;
        padding: 8px 12px; border-radius: 6px; text-decoration: none;
        margin-bottom: 2px; transition: background 0.15s, color 0.15s;
    }
    .cat-sidebar-item:hover { background: rgba(255,255,255,0.03); }
    .cat-sidebar-item.active { background: rgba(255,255,255,0.06); }
    .cat-sidebar-label { font-size: 14px; color: #94A3B8; flex: 1; }
    .cat-sidebar-item:hover .cat-sidebar-label { color: #F8FAFC; }
    .cat-sidebar-item.active .cat-sidebar-label { color: #FFFFFF; font-weight: 500; }
    .cat-sidebar-count { font-size: 12px; color: #64748B; }
    .cat-sidebar-item.active .cat-sidebar-count { color: #94A3B8; }

    .search-outer { margin: 0; }
    .search-row { display: flex; align-items: center; gap: 8px; }

    .kw-bar { flex: 1; display: flex; align-items: center; gap: 0;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
        padding: 10px 14px;
        box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset; transition: all 0.2s; }
    .kw-bar:focus-within { border-color: rgba(56,189,248,0.35);
        box-shadow: 0 0 0 1px rgba(2,132,199,0.12); }
    .kw-icon { color: #64748B; flex-shrink: 0; margin-right: 10px; }
    .kw-input { flex: 1; border: none; outline: none; background: transparent;
        font-family: 'Inter', sans-serif; font-size: 14px; color: #F1F5F9; min-width: 0; }
    .kw-input::placeholder { color: #64748B; }
    .ai-pill-btn { display: flex; align-items: center; gap: 6px; flex-shrink: 0;
        background: linear-gradient(135deg, rgba(99,102,241,0.88) 0%, rgba(139,92,246,0.85) 55%, rgba(236,72,153,0.78) 100%);
        color: #fff; border: none; border-radius: 10px; padding: 10px 18px;
        font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Inter', sans-serif;
        height: 44px;
        white-space: nowrap; letter-spacing: 0.3px; transition: opacity 0.15s; }
    .ai-pill-btn:hover { opacity: 0.9; }

    .filter-btn { width: 40px; height: 40px; flex-shrink: 0; border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04); cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        color: #94A3B8; transition: all 0.15s;
        box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset; position: relative; }
    .filter-btn:hover { border-color: rgba(255,255,255,0.2); color: #CBD5E1; background: rgba(255,255,255,0.06); }
    .filter-btn.on { border-color: rgba(56,189,248,0.35); color: #7dd3fc; background: rgba(2,132,199,0.12); }
    .filter-btn .filter-dot { display: none; position: absolute; top: 6px; right: 6px;
        width: 6px; height: 6px; border-radius: 50%; background: #38bdf8; }
    .filter-btn.has-filters .filter-dot { display: block; }

    .filter-panel { display: block; margin-top: 16px; padding: 14px 16px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06); border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .filter-row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
    .filter-row:last-child { margin-bottom: 0; }
    .filter-label { font-size: 11px; font-weight: 700; color: #64748B;
        text-transform: uppercase; letter-spacing: 0.08em; min-width: 72px; }

    .ai-bar { flex: 1; display: none; flex-direction: column; gap: 6px; }
    .ai-bar.active { display: flex; }
    .ai-bar-inner { display: flex; align-items: center; gap: 0;
        border-radius: 12px; padding: 10px 6px 10px 16px;
        border: 2px solid transparent;
        background-image:
            linear-gradient(rgba(15,23,42,0.95), rgba(15,23,42,0.95)),
            linear-gradient(135deg, #6366F1, #8B5CF6, #EC4899);
        background-origin: border-box; background-clip: padding-box, border-box;
        box-shadow: 0 4px 20px rgba(99,102,241,0.12);
        animation: aiExpand 0.2s ease; }
    @keyframes aiExpand {
        from { opacity: 0; transform: scaleY(0.9); }
        to   { opacity: 1; transform: scaleY(1); } }
    .ai-sparkle { font-size: 15px; margin-right: 10px; flex-shrink: 0; }
    .ai-query-input { flex: 1; border: none; outline: none; background: transparent;
        font-family: 'Inter', sans-serif; font-size: 14px; color: #F1F5F9; min-width: 0; }
    .ai-query-input::placeholder { color: #94A3B8; }
    .ai-submit-btn { flex-shrink: 0;
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: #fff; border: none; border-radius: 8px; padding: 8px 16px;
        font-size: 13px; font-weight: 600; cursor: pointer;
        font-family: 'Inter', sans-serif; transition: opacity 0.15s; white-space: nowrap; }
    .ai-submit-btn:hover { opacity: 0.88; }
    .ai-back-btn { background: none; border: none; color: #94A3B8; font-size: 12px;
        cursor: pointer; font-family: 'Inter', sans-serif; padding: 0;
        text-align: left; transition: color 0.15s; }
    .ai-back-btn:hover { color: #CBD5E1; }

    .thinking-bar { display: none; align-items: center; gap: 10px;
        margin-top: 8px; padding: 10px 14px;
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(139,92,246,0.2); border-radius: 10px; }
    .thinking-bar.active { display: flex; }
    .thinking-dots { display: flex; gap: 4px; align-items: center; }
    @keyframes dotPulse {
        0%, 80%, 100% { transform: scale(0.7); opacity: 0.35; }
        40%            { transform: scale(1.1); opacity: 1; } }
    .thinking-dot { width: 6px; height: 6px; border-radius: 50%;
        background: linear-gradient(135deg, #6366F1, #EC4899);
        animation: dotPulse 1.4s ease-in-out infinite; }
    .thinking-dot:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dot:nth-child(3) { animation-delay: 0.4s; }
    .thinking-msg { font-size: 13px; color: #a5b4fc; font-weight: 500; }

    .filters { display: flex; align-items: center; gap: 16px; margin: 12px 0; flex-wrap: wrap; }
    .filter-group { display: flex; align-items: center; gap: 5px; }
    .chip { padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 500;
        text-decoration: none; color: #94A3B8;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.04); cursor: pointer; transition: all 0.12s; white-space: nowrap; }
    .chip:hover { color: #E2E8F0; border-color: rgba(255,255,255,0.16); background: rgba(255,255,255,0.06); }
    .chip.on { background: rgba(2,132,199,0.15); color: #7dd3fc; border-color: rgba(56,189,248,0.25); font-weight: 600; }

    .ds-list-box { background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; overflow: hidden;
        box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset; }
    .ds-count-bar { display: flex; align-items: center; justify-content: space-between;
        padding: 8px 16px; border-bottom: 1px solid rgba(255,255,255,0.06);
        font-size: 12px; color: #94A3B8; background: rgba(0,0,0,0.2); }
    .per-page-wrap { display: flex; align-items: center; gap: 6px; }
    .per-page-label { font-size: 11px; color: #64748B; }
    .per-page-select { font-size: 12px; color: #CBD5E1; background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 4px 8px;
        cursor: pointer; font-family: 'Inter', sans-serif; outline: none; }
    .per-page-select:focus { border-color: rgba(56,189,248,0.35); }
    .ds-pagination { display: flex; align-items: center; justify-content: center;
        gap: 4px; padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.06); }
    .page-btn { display: inline-flex; align-items: center; justify-content: center;
        min-width: 32px; height: 32px; padding: 0 8px; border-radius: 6px;
        font-size: 13px; font-weight: 500; text-decoration: none;
        border: 1px solid rgba(255,255,255,0.1); color: #94A3B8; background: rgba(255,255,255,0.04);
        cursor: pointer; transition: all 0.12s; }
    .page-btn:hover { border-color: rgba(255,255,255,0.18); background: rgba(255,255,255,0.08); color: #E2E8F0; }
    .page-btn.active { background: #0284C7; border-color: #0284C7; color: #FFFFFF; font-weight: 600; }
    .page-btn.disabled { color: #475569; cursor: default; pointer-events: none; border-color: rgba(255,255,255,0.05); }
    .page-ellipsis { color: #64748B; font-size: 13px; padding: 0 4px; }
    .ds-list { display: flex; flex-direction: column; }
    .ds-row { display: flex; align-items: center; gap: 10px; padding: 11px 14px;
        border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.1s; }
    .ds-row:last-child { border-bottom: none; }
    .ds-row:hover { background: rgba(255,255,255,0.04); }

    .ds-row-mid { flex: 1; min-width: 0; }
    .ds-name { font-size: 14px; font-weight: 600; color: #F1F5F9; text-decoration: none;
        display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; }
    .ds-name:hover { color: #7dd3fc; }
    .ds-meta { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
    .ds-cat-label { font-size: 12px; color: #94A3B8; }
    .ds-sep { color: #64748B; font-size: 12px; }
    .ds-prov { font-size: 12px; color: #94A3B8; white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis; max-width: 220px; }
    .ds-desc { font-size: 12px; color: #94A3B8; margin-top: 2px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .ds-row-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
    .badge { padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-api  { background: rgba(2,132,199,0.2); color: #7dd3fc; border: 1px solid rgba(56,189,248,0.2); }
    .badge-sf   { background: rgba(59,130,246,0.15); color: #93c5fd; border: 1px solid rgba(59,130,246,0.2); }
    .badge-freq { background: rgba(148,163,184,0.12); color: #94A3B8; font-weight: 500; border: 1px solid rgba(148,163,184,0.15); }

    .fav-btn { background: transparent; border: none; cursor: pointer;
        font-size: 20px; color: #64748B; padding: 3px 6px; line-height: 1;
        transition: color 0.15s; flex-shrink: 0; }
    .fav-btn:hover { color: #F59E0B; }
    .fav-btn.on { color: #F59E0B; }

    .add-btn {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.12);
        color: #CBD5E1; font-size: 12px; font-weight: 600; padding: 4px 11px;
        border-radius: 6px; cursor: pointer; font-family: 'Inter', sans-serif;
        transition: all 0.15s; white-space: nowrap; flex-shrink: 0; }
    .add-btn:hover { border-color: rgba(56,189,248,0.35); color: #7dd3fc; background: rgba(2,132,199,0.1); }
    .added-badge { font-size: 12px; font-weight: 600; color: #6ee7b7; padding: 3px 6px;
        white-space: nowrap; }
    .remove-link { background: transparent; border: none; color: #64748B; font-size: 11px;
        cursor: pointer; padding: 0; font-family: 'Inter', sans-serif; }
    .remove-link:hover { color: #EF4444; }

    .ai-reason { font-size: 12px; color: #94A3B8; margin-top: 3px;
        border-left: 2px solid rgba(56,189,248,0.4); padding-left: 8px; line-height: 1.5; }
    .ai-banner { background: rgba(2,132,199,0.1);
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 8px; padding: 10px 14px; margin-bottom: 14px;
        font-size: 13px; color: #7dd3fc; }
    .empty-msg { padding: 40px 20px; color: #94A3B8; font-size: 14px; text-align: center; }

    .fav-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
    .fav-page-title { font-size: 22px; font-weight: 600; color: #F8FAFC; letter-spacing: -0.03em; }
    .fav-new-form { display: flex; gap: 8px; align-items: center; }
    .fav-new-input { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: #F1F5F9;
        padding: 8px 12px; border-radius: 8px; font-family: 'Inter', sans-serif;
        font-size: 13px; outline: none; transition: border-color 0.2s; width: 180px; }
    .fav-new-input:focus { border-color: rgba(56,189,248,0.35); box-shadow: 0 0 0 1px rgba(2,132,199,0.12); }
    .fav-new-input::placeholder { color: #64748B; }
    .fav-create-btn { background: #0284C7; color: #fff; border: none;
        padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 600;
        cursor: pointer; font-family: 'Inter', sans-serif; white-space: nowrap;
        transition: background 0.15s; }
    .fav-create-btn:hover { background: #0369A1; }

    .fav-selector-wrap { padding: 0 24px; margin-bottom: 32px; max-width: 420px; }
    .fav-list-select {
        width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 36px 10px 14px; font-family: 'Inter', sans-serif;
        font-size: 14px; color: #F1F5F9; cursor: pointer; outline: none;
        transition: border-color 0.2s; appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2394A3B8'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
        background-repeat: no-repeat; background-position: right 12px center; background-size: 16px;
    }
    .fav-list-select:focus { border-color: rgba(56,189,248,0.35); box-shadow: 0 0 0 1px rgba(2,132,199,0.12); }

    .fav-tab-count { background: rgba(255,255,255,0.08); color: #94A3B8; font-size: 11px;
        font-weight: 700; padding: 1px 7px; border-radius: 999px; }
    .fav-tab.active .fav-tab-count { background: rgba(2,132,199,0.12); color: #7dd3fc; }

    .fav-content { display: none; }
    .fav-content.active { display: block; }
    .fav-content-header { display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 12px; }
    .fav-content-name { font-size: 15px; font-weight: 600; color: #F1F5F9; }
    .fav-delete-btn { background: transparent; border: 1px solid rgba(255,255,255,0.12); color: #94A3B8;
        padding: 5px 11px; border-radius: 6px; font-size: 12px; cursor: pointer;
        font-family: 'Inter', sans-serif; transition: all 0.15s; }
    .fav-delete-btn:hover { border-color: rgba(252,165,165,0.4); color: #EF4444; background: rgba(239,68,68,0.08); }

    .fav-ds-row { display: flex; align-items: center; gap: 12px; padding: 10px 14px;
        border-bottom: 1px solid rgba(255,255,255,0.05); }
    .fav-ds-row:last-child { border-bottom: none; }
    .fav-ds-row:hover { background: rgba(255,255,255,0.04); }
    .fav-ds-title { flex: 1; font-size: 14px; font-weight: 500; color: #F1F5F9;
        text-decoration: none; }
    .fav-ds-title:hover { color: #7dd3fc; }
    .fav-ds-meta { font-size: 12px; color: #94A3B8; }
    .fav-remove-btn { background: transparent; border: none; color: #64748B;
        font-size: 18px; line-height: 1; cursor: pointer; padding: 2px 6px;
        border-radius: 4px; transition: all 0.15s; flex-shrink: 0; }
    .fav-remove-btn:hover { background: rgba(239,68,68,0.12); color: #EF4444; }

    @media (max-width: 1100px) {
        .cat-main-col { padding: 24px 20px; }
        .cat-content-grid { grid-template-columns: 1fr; gap: 16px; }
    }
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
        for row in db_select("dataset_integrations", {"user_id": user_id}):
            added.add(row["dataset_slug"])
    except Exception:
        pass
    try:
        for row in db_select("favourite_items", {"user_id": user_id}):
            favs.add(row["dataset_slug"])
    except Exception:
        pass
    return added, favs


# ── Row-level components ──────────────────────────────────────────────────────

def _fav_btn(slug, is_fav, oob=False):
    attrs = {"hx_swap_oob": "true"} if oob else {}
    return Button(
        "★" if is_fav else "☆",
        type="button",
        hx_get=f"/catalog/{slug}/favourite-modal",
        hx_target="#modal-root",
        id=f"fav-{slug}",
        cls=f"fav-btn {'on' if is_fav else ''}",
        title="Save to Favourites",
        **attrs
    )


def _add_btn(slug, is_added, oob=False):
    attrs = {"hx_swap_oob": "true"} if oob else {}
    if is_added:
        return Button(
            "✓ Added",
            hx_get=f"/catalog/{slug}/integration-modal",
            hx_target="#modal-root",
            id=f"add-{slug}",
            cls="add-btn",
            style="border-color: rgba(16,185,129,0.45); color: #6ee7b7; background: rgba(16,185,129,0.12);",
            title="Edit dataset integrations",
            **attrs
        )
    return Button(
        "+ Add",
        hx_get=f"/catalog/{slug}/integration-modal",
        hx_target="#modal-root",
        id=f"add-{slug}",
        cls="add-btn",
        title="Add this dataset to your integrations",
        **attrs
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
        _fav_btn(slug, is_fav),
        _add_btn(slug, is_added),
        cls="ds-row-right"
    )
    return Div(mid, right, cls="ds-row")


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
            htmx.ajax('GET', '/catalog/{slug}/fav-btn', {{target: '#fav-{slug}', swap: 'outerHTML'}});
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

# ── Integration modal ─────────────────────────────────────────────────────────

def _int_checkbox(int_id, slug, in_list, int_name):
    """A single integration row inside the integration modal — toggleable via HTMX."""
    return Div(
        Input(
            type="checkbox",
            checked=in_list,
            hx_post=f"/integrations/{int_id}/toggle?slug={slug}",
            hx_trigger="change",
            hx_target=f"#icheck-{int_id}",
            hx_swap="outerHTML",
            hx_include="this",
        ),
        Span(int_name, cls="list-check-name"),
        id=f"icheck-{int_id}",
        cls="list-check-row",
    )

def IntegrationModal(slug, dataset_title, project_id):
    try:
        ints = db_select("integrations", {"project_id": project_id})
    except Exception:
        ints = []

    try:
        items = db_select("dataset_integrations", {"dataset_slug": slug})
        valid_int_ids = {i["id"] for i in ints}
        in_int_ids = {item["integration_id"] for item in items if item["integration_id"] in valid_int_ids}
    except Exception:
        in_int_ids = set()

    int_rows = [
        _int_checkbox(i["id"], slug, i["id"] in in_int_ids, i["name"])
        for i in ints
    ]

    empty_msg = Div(
        P("No integrations created yet.", cls="modal-empty"),
        A("Create connection targets →", href="/integrations", style="font-size: 13px; color: #0284C7; text-decoration: none;")
    ) if not ints else None

    close_and_update = Script(f"""
        document.getElementById('modal-done').addEventListener('click', function() {{
            htmx.ajax('GET', '/catalog/{slug}/add-btn', {{target: '#add-{slug}', swap: 'outerHTML'}});
            document.getElementById('modal-root').innerHTML = '';
        }});
    """)

    return Div(
        Div(style="position:absolute;inset:0;",
            onclick="document.getElementById('modal-root').innerHTML=''"),
        Div(
            P("🔌 Connect Dataset", cls="modal-title"),
            P(dataset_title, cls="modal-sub"),
            Hr(cls="modal-divider"),
            Div(empty_msg, *int_rows, id="modal-ints") if empty_msg or int_rows else None,
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

def _sidebar(counts, active_cat, total):
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
        if cat == "Other": continue
        items.append(A(
            Span(cat, cls="cat-sidebar-label"),
            Span(str(counts[cat]), cls="cat-sidebar-count"),
            href=f"/catalog?category={cat}",
            cls=f"cat-sidebar-item {'active' if cat == active_cat else ''}",
        ))
    return Div(*items, cls="cat-sidebar")


# ── Search area ───────────────────────────────────────────────────────────────

def _search_area(q, category, access_f, freq_f):
    search_svg = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>')
    filter_svg = NotStr('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><line x1="4" y1="6" x2="20" y2="6"/><circle cx="9" cy="6" r="2.5" fill="#475569"/><line x1="4" y1="12" x2="20" y2="12"/><circle cx="16" cy="12" r="2.5" fill="#475569"/><line x1="4" y1="18" x2="20" y2="18"/><circle cx="11" cy="18" r="2.5" fill="#475569"/></svg>')

    has_filters = bool(access_f or freq_f)
    filter_btn_cls = "filter-btn" + (" on has-filters" if has_filters else "")

    kw_bar = Div(
        Div(search_svg, cls="kw-icon"),
        Input(type="search", name="q", value=q,
              placeholder="Search datasets…",
              cls="kw-input",
              hx_get="/catalog/search",
              hx_trigger="input changed delay:280ms, search",
              hx_target="#catalog-body",
              hx_include="[name='q'],[name='category'],[name='access'],[name='freq']",
              hx_push_url="true"),
        Input(type="hidden", name="category", value=category),
        Input(type="hidden", name="access",   value=access_f),
        Input(type="hidden", name="freq",     value=freq_f),
        id="kw-bar", cls="kw-bar"
    )

    ai_btn = Button(NotStr("✦ AI Search"), type="button", cls="ai-pill-btn", onclick="activateAI()")

    ai_bar = Form(
        Div(
            Span("✦", cls="ai-sparkle"),
            Input(type="text", name="query",
                  placeholder="Describe what you're looking for, e.g. 'company directors for KYC'…",
                  cls="ai-query-input", id="ai-query-input"),
            Button("Search →", type="submit", cls="ai-submit-btn"),
            cls="ai-bar-inner"
        ),
        Button("← back to keyword search", type="button", cls="ai-back-btn", onclick="deactivateAI()"),
        hx_post="/catalog/ai-search",
        hx_target="#catalog-body",
        cls="ai-bar", id="ai-bar"
    )

    # Filter chips for the panel
    def chip(label, param, value, current):
        is_on = (current == value) or (value == "" and not current)
        a = value if param == "access" else access_f
        f = value if param == "freq"   else freq_f
        qs = f"q={q}&category={category}&access={a}&freq={f}"
        return A(label,
                 hx_get=f"/catalog/search?{qs}",
                 hx_target="#catalog-body",
                 hx_push_url=f"/catalog?{qs}",
                 cls=f"chip {'on' if is_on else ''}")

    filter_panel = Div(
        Div(
            Span("Access", cls="filter-label"),
            *[chip(l, "access", v, access_f) for l, v in ACCESS_FILTERS],
            cls="filter-row"
        ),
        Div(
            Span("Frequency", cls="filter-label"),
            *[chip(l, "freq", v, freq_f) for l, v in FREQ_FILTERS],
            cls="filter-row"
        ),
        id="filter-panel",
        cls="filter-panel"
    )

    thinking_bar = Div(
        Div(Div(cls="thinking-dot"), Div(cls="thinking-dot"), Div(cls="thinking-dot"),
            cls="thinking-dots"),
        Span("Searching...", id="thinking-msg", cls="thinking-msg"),
        id="thinking-bar", cls="thinking-bar"
    )

    script = Script("""
        const _thinkMsgs = ['Searching...','Thinking...','Analysing datasets...','Finding matches...','Almost there...'];
        let _thinkIdx = 0, _thinkTimer = null;

        function activateAI() {
            document.getElementById('kw-bar-wrap').style.display = 'none';
            document.getElementById('ai-bar').classList.add('active');
            document.getElementById('ai-query-input').focus();
        }
        function deactivateAI() {
            document.getElementById('kw-bar-wrap').style.display = '';
            document.getElementById('ai-bar').classList.remove('active');
            document.getElementById('thinking-bar').classList.remove('active');
            clearInterval(_thinkTimer);
        }
        document.body.addEventListener('htmx:beforeRequest', function(e) {
            if (e.target.id === 'ai-bar') {
                document.getElementById('thinking-bar').classList.add('active');
                _thinkIdx = 0;
                _thinkTimer = setInterval(function() {
                    document.getElementById('thinking-msg').textContent =
                        _thinkMsgs[_thinkIdx++ % _thinkMsgs.length];
                }, 750);
            }
        });
        document.body.addEventListener('htmx:afterRequest', function(e) {
            if (e.target.id === 'ai-bar') {
                document.getElementById('thinking-bar').classList.remove('active');
                clearInterval(_thinkTimer);
            }
        });
    """)

    return Div(
        Div(
            Div(kw_bar, ai_btn, cls="search-row", id="kw-bar-wrap"),
            ai_bar,
            cls="search-row"
        ),
        filter_panel,
        thinking_bar,
        script,
        cls="search-outer"
    )


# ── List body ─────────────────────────────────────────────────────────────────

def _page_nums(page, total_pages):
    if total_pages <= 7:
        return list(range(1, total_pages + 1))
    pages = {1, total_pages}
    for p in range(max(1, page - 2), min(total_pages + 1, page + 3)):
        pages.add(p)
    result, prev = [], None
    for p in sorted(pages):
        if prev is not None and p - prev > 1:
            result.append(None)
        result.append(p)
        prev = p
    return result


def _list_body(page_datasets, total, added, favs, heading, subtext, page=1, per_page=25, q="", category="", access_f="", freq_f=""):
    if not page_datasets:
        return Div(
            Div(H1(heading, style="font-size:18px;font-weight:600;color:#F8FAFC;letter-spacing:-0.03em;"),
                P(subtext, style="font-size:13px;color:#94A3B8;margin-top:3px;"),
                style="margin-bottom:14px;"),
            Div(P("No datasets match.", cls="empty-msg"), cls="ds-list-box"),
        )

    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    qs_base = f"q={q}&category={category}&access={access_f}&freq={freq_f}"

    per_page_select = Select(
        *[Option(str(n), value=str(n), selected=(n == per_page)) for n in [25, 50, 100, 200]],
        cls="per-page-select",
        onchange=f"htmx.ajax('GET', '/catalog/search?{qs_base}&page=1&per_page=' + this.value, "
                 f"{{target:'#catalog-body', pushUrl:'/catalog?{qs_base}&page=1&per_page=' + this.value}})"
    )

    count_bar = Div(
        Span(f"{total} dataset{'s' if total != 1 else ''}"),
        Div(Span("View", cls="per-page-label"), per_page_select, cls="per-page-wrap"),
        cls="ds-count-bar"
    )

    def page_link(label, page_n, is_active=False, is_disabled=False):
        if is_disabled:
            return Span(label, cls="page-btn disabled")
        qs = f"{qs_base}&page={page_n}&per_page={per_page}"
        return A(label,
                 hx_get=f"/catalog/search?{qs}",
                 hx_target="#catalog-body",
                 hx_push_url=f"/catalog?{qs}",
                 cls=f"page-btn {'active' if is_active else ''}")

    page_items = [page_link("‹", page - 1, is_disabled=(page == 1))]
    for p in _page_nums(page, total_pages):
        if p is None:
            page_items.append(Span("…", cls="page-ellipsis"))
        else:
            page_items.append(page_link(str(p), p, is_active=(p == page)))
    page_items.append(page_link("›", page + 1, is_disabled=(page == total_pages)))

    return Div(
        Div(H1(heading, style="font-size:18px;font-weight:600;color:#F8FAFC;letter-spacing:-0.03em;"),
            P(subtext, style="font-size:13px;color:#94A3B8;margin-top:3px;"),
            style="margin-bottom:14px;"),
        Div(
            count_bar,
            Div(*[_list_row(d, is_added=d.get("slug") in added, is_fav=d.get("slug") in favs)
                  for d in page_datasets], cls="ds-list"),
            Div(*page_items, cls="ds-pagination") if total_pages > 1 else None,
            cls="ds-list-box"
        )
    )


# ── Public components ─────────────────────────────────────────────────────────

def DataCatalog(category="", q="", user_id="", access_filter="", freq_filter="", page=1, per_page=25):
    from app.supabase_db import get_datasets_paginated, get_category_counts
    try:
        datasets, total_matches = get_datasets_paginated(category, q, access_filter, freq_filter, page, per_page)
        counts, total_all = get_category_counts()
    except Exception:
        datasets, counts, total_matches, total_all = [], {}, 0, 0

    added, favs = _fetch_user_sets(user_id)

    heading = f'Results for "{q}"' if q else (category or "London Database")
    subtext = (f"{total_matches} dataset{'s' if total_matches != 1 else ''} found"
               if (q or category or access_filter or freq_filter)
               else f"{total_matches} datasets — growing continuously")

    return Div(
        CATALOG_STYLE,
        Div(
            _sidebar(counts, category, total_all),
            Div(
                Div(
                    Div(
                        _search_area(q, category, access_filter, freq_filter),
                        cls="cat-controls-col"
                    ),
                    Div(
                        _list_body(datasets, total_matches, added, favs, heading, subtext,
                                   page=page, per_page=per_page,
                                   q=q, category=category, access_f=access_filter, freq_f=freq_filter),
                        id="catalog-body", cls="cat-main cat-results-col"
                    ),
                    cls="cat-content-grid"
                ),
                cls="cat-main-col"
            ),
            cls="cat-wrap"
        )
    )


def SearchCatalogResults(q="", category="", user_id="", access_filter="", freq_filter="", page=1, per_page=25):
    from app.supabase_db import get_datasets_paginated
    try:
        datasets, total_matches = get_datasets_paginated(category, q, access_filter, freq_filter, page, per_page)
    except Exception:
        datasets, total_matches = [], 0

    added, favs = _fetch_user_sets(user_id)
    heading = f'Results for "{q}"' if q else (category or "London Database")
    subtext = (f"{total_matches} dataset{'s' if total_matches != 1 else ''} found"
               if (q or category or access_filter or freq_filter)
               else f"{total_matches} datasets — growing continuously")
    return _list_body(datasets, total_matches, added, favs, heading, subtext,
                      page=page, per_page=per_page,
                      q=q, category=category, access_f=access_filter, freq_f=freq_filter)


def FavouritesView(user_id=""):
    try:
        lists = db_select("favourite_lists", {"user_id": user_id})
    except Exception:
        lists = []

    try:
        all_datasets = db_select("datasets")
    except Exception:
        all_datasets = []
    ds_map = {d["slug"]: d for d in all_datasets}

    # Header with create-list form
    new_list_form = Form(
        Input(type="text", name="name", placeholder="New list name…",
              required=True, cls="fav-new-input"),
        Button("+ Create", type="submit", cls="fav-create-btn"),
        hx_post="/favourite-lists/create",
        hx_on__after_request="if(event.detail.successful) window.location.reload()",
        cls="fav-new-form"
    )
    header = Div(
        H1("Favourites", cls="fav-page-title"),
        new_list_form,
        cls="fav-header"
    )

    if not lists:
        return Div(
            CATALOG_STYLE,
            header,
            Div(
                P("No lists yet.", style="font-size:15px;font-weight:600;color:#F8FAFC;margin-bottom:8px;"),
                P("Create a list above, then star ☆ any dataset in the catalog to add it.",
                  style="font-size:14px;color:#64748B;line-height:1.6;margin-bottom:20px;"),
                A("Browse the catalog →", href="/catalog",
                  style="color:#0284C7;font-size:14px;font-weight:600;text-decoration:none;"),
                cls="empty-msg", style="text-align:left;padding:32px 24px;"
            )
        )

    # Build options and content panels
    options, panels = [], []
    for i, lst in enumerate(lists):
        try:
            items = db_select("favourite_items", {"list_id": lst["id"]})
        except Exception:
            items = []
        slugs = [item["dataset_slug"] for item in items]
        datasets = [ds_map[s] for s in slugs if s in ds_map]
        is_first = (i == 0)
        list_id = lst["id"]

        options.append(Option(f"{lst['name']} ({len(datasets)})", value=list_id, selected=is_first))

        if datasets:
            rows = [Div(
                Span("★", style="color:#F59E0B;font-size:16px;flex-shrink:0;"),
                A(d.get("title") or d["slug"], href=f"/catalog/{d['slug']}", cls="fav-ds-title"),
                Span(d.get("category") or "", cls="fav-ds-meta"),
                Form(
                    Button("×", type="submit", cls="fav-remove-btn", title="Remove from list"),
                    action=f"/favourite-lists/{list_id}/items/{d['slug']}/remove",
                    method="POST"
                ),
                cls="fav-ds-row"
            ) for d in datasets]
        else:
            rows = [P("No datasets in this list yet. Star ☆ datasets in the catalog to add them.",
                      style="color:#94A3B8;font-size:13px;padding:20px 14px;")]

        panels.append(Div(
            Div(
                Span(lst["name"], cls="fav-content-name"),
                Form(Button("Delete list", type="submit", cls="fav-delete-btn"),
                     action=f"/favourite-lists/{list_id}/delete", method="POST"),
                cls="fav-content-header"
            ),
            Div(*rows, cls="ds-list-box"),
            id=f"fav-content-{list_id}",
            cls=f"fav-content {'active' if is_first else ''}"
        ))

    return Div(
        CATALOG_STYLE,
        header,
        Div(
            Label("Select Collection:", style="font-size:12px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:8px; display:block;"),
            Select(*options, cls="fav-list-select", onchange="selectFavList(this.value)"),
            cls="fav-selector-wrap"
        ),
        *panels,
        Script("""
            function selectFavList(id) {
                document.querySelectorAll('.fav-content').forEach(c => c.classList.remove('active'));
                document.getElementById('fav-content-' + id).classList.add('active');
            }
        """)
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
