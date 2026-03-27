import json
from fasthtml.common import *
from app.supabase_db import db_select

FREQ_SHORT = {
    "Real-time": "Real-time", "Streaming": "Real-time",
    "Hourly": "Hourly", "Daily": "Daily", "Weekly": "Weekly",
    "Monthly": "Monthly", "Quarterly": "Quarterly", "Annual": "Annual",
    "Irregular": "Irregular", "One-off": "One-off",
}
FREQ_FILTERS = [
    ("Real-time", "Real-time"),
    ("Hourly", "Hourly"),
    ("Daily", "Daily"),
    ("Weekly", "Weekly"),
    ("Monthly", "Monthly"),
    ("Quarterly", "Quarterly"),
    ("Yearly", "Yearly"),
    ("Less than once a year", "Less than once a year"),
]
SIZE_FILTERS = [
    ("Up to 1k rows", "le_1k"),
    ("Up to 10k rows", "le_10k"),
    ("Up to 100k rows", "le_100k"),
    ("Up to 1m rows", "le_1m"),
    ("Up to 10m rows", "le_10m"),
    ("Up to 100m rows", "le_100m"),
    ("100m+ rows", "gt_100m"),
]
SORT_OPTIONS = [
    ("Most recently updated", "recent"),
    ("Name (A to Z)", "name_asc"),
    ("Name (Z to A)", "name_desc"),
    ("Size (MB): largest first", "size_desc"),
    ("Size (MB): smallest first", "size_asc"),
    ("Row count: largest first", "rows_desc"),
    ("Row count: smallest first", "rows_asc"),
]

CATALOG_STYLE = Style("""
    /* Dark surfaces — aligned with dashboard (no stark white on #080a0f) */
    .cat-wrap { display: flex; width: 100%; min-height: calc(100vh - 60px); align-items: stretch; background-color: var(--bg-page); }
    .cat-sidebar {
        width: 240px; flex-shrink: 0;
        position: sticky;
        top: 60px;
        height: calc(100vh - 60px);
        overflow-y: auto;
        -ms-overflow-style: none;
        scrollbar-width: none;
        padding: 40px 16px 24px;
        background: var(--bg-elevated);
        border-right: 1px solid var(--border);
    }
    .cat-sidebar::-webkit-scrollbar { width: 0; height: 0; display: none; }
    .cat-main {
        min-width: 0; flex: 1; display: flex; flex-direction: column; width: 100%;
    }
    .cat-results-col {
        flex: 1; min-width: 0; padding: 32px 20px;
        position: sticky; top: 60px; height: calc(100vh - 60px);
        overflow-y: auto;
        background: var(--bg-page);
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    .cat-results-col::-webkit-scrollbar { width: 0; height: 0; display: none; }
    .cat-controls-col {
        width: 340px; min-width: 280px; flex-shrink: 0; padding: 32px 20px;
        position: sticky; top: 60px; height: calc(100vh - 60px);
        overflow-y: auto;
        background: var(--bg-page);
        -ms-overflow-style: none;
        scrollbar-width: none;
        border-left: 1px solid var(--border);
    }
    .cat-controls-col::-webkit-scrollbar { width: 0; height: 0; display: none; }
    .cat-splitter {
        width: 12px;
        cursor: col-resize;
        flex-shrink: 0;
        position: relative;
        user-select: none;
        touch-action: none;
    }
    .cat-splitter::before {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 50%;
        width: 1px;
        transform: translateX(-50%);
        background: var(--border);
    }
    .cat-splitter:hover::before,
    .cat-splitter.dragging::before {
        background: var(--accent);
    }

    .cat-sidebar-title {
        font-family: var(--font-display); font-size: 11px; font-weight: 700;
        color: var(--text-faint); text-transform: uppercase; letter-spacing: 0.1em;
        padding-left: 4px; margin-bottom: 12px;
    }
    .cat-sidebar-item {
        display: flex; align-items: center; justify-content: space-between; gap: 8px;
        padding: 8px 12px; border-radius: 6px; text-decoration: none;
        margin-bottom: 2px; transition: background 0.15s, color 0.15s;
    }
    .cat-sidebar-item:hover { background: var(--bg-surface); }
    .cat-sidebar-item.active { background: var(--bg-muted); }
    .cat-sidebar-label { font-size: 14px; color: var(--text-muted); flex: 1; }
    .cat-sidebar-item:hover .cat-sidebar-label { color: var(--text-main); }
    .cat-sidebar-item.active .cat-sidebar-label { color: var(--text-main); font-weight: 500; }
    .cat-sidebar-count { font-size: 12px; color: var(--text-faint); }
    .cat-sidebar-item.active .cat-sidebar-count { color: var(--text-muted); }

    .cat-header-row {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }
    .cat-header-text { min-width: 0; flex: 1; }
    .cat-fav-select-wrap {
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        gap: 5px;
        align-items: flex-end;
    }
    .cat-fav-select-label {
        font-size: 11px;
        font-weight: 700;
        color: var(--text-faint);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .cat-fav-select {
        min-width: 200px;
        max-width: min(280px, 100%);
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: var(--bg-surface);
        color: var(--text-main);
        font-size: 13px;
        font-family: var(--font-body);
        outline: none;
        cursor: pointer;
    }
    .cat-fav-select:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent-light);
    }

    .search-outer { margin: 0; }
    .controls-slicer {
        display: flex; align-items: center;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px; padding: 3px; gap: 2px;
        box-shadow: inset 0 1px 1px rgba(0,0,0,0.1);
        margin-bottom: 14px;
    }
    .controls-slicer-btn {
        flex: 1;
        display: flex; align-items: center; justify-content: center;
        padding: 7px 12px; border-radius: 9px;
        border: 1px solid transparent; background: transparent;
        color: var(--text-muted); font-family: var(--font-body);
        font-size: 13px; font-weight: 500; cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
    }
    .controls-slicer-btn:hover {
        color: var(--text-main);
        background: var(--bg-muted);
    }
    .controls-slicer-btn.active {
        color: var(--text-main);
        background: var(--accent-light);
        border-color: var(--accent);
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .controls-panel { display: none; }
    .controls-panel.active { display: block; }
    .search-row { display: flex; align-items: center; gap: 8px; }
    .kw-search-wrap { margin-bottom: 14px; width: 100%; min-width: 0; }

    .kw-bar { flex: 1; display: flex; align-items: center; gap: 0;
        background: var(--bg-surface);
        border: 1px solid var(--border); border-radius: 12px;
        padding: 10px 14px;
        box-shadow: 0 1px 0 var(--border-subtle) inset; transition: all 0.2s; }
    .kw-bar:focus-within { border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent-light); }
    .kw-icon { color: var(--text-faint); flex-shrink: 0; margin-right: 10px; }
    .kw-input { flex: 1; border: none; outline: none; background: transparent;
        font-family: var(--font-body); font-size: 14px; color: var(--text-main); min-width: 0; }
    .kw-input::placeholder { color: var(--text-faint); }
    .ai-pill-btn { display: flex; align-items: center; gap: 6px; flex-shrink: 0;
        background: linear-gradient(135deg, rgba(99,102,241,0.88) 0%, rgba(139,92,246,0.85) 55%, rgba(236,72,153,0.78) 100%);
        color: #fff; border: none; border-radius: 10px; padding: 10px 18px;
        font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Inter', sans-serif;
        height: 44px;
        white-space: nowrap; letter-spacing: 0.3px; transition: opacity 0.15s; }
    .ai-pill-btn:hover { opacity: 0.9; }

    .filter-btn { width: 40px; height: 40px; flex-shrink: 0; border-radius: 10px;
        border: 1px solid var(--border); background: var(--bg-surface); cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        color: var(--text-muted); transition: all 0.15s;
        box-shadow: 0 1px 0 var(--border-subtle) inset; position: relative; }
    .filter-btn:hover { border-color: var(--text-muted); color: var(--text-main); background: var(--bg-muted); }
    .filter-btn.on { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
    .filter-btn .filter-dot { display: none; position: absolute; top: 6px; right: 6px;
        width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
    .filter-btn.has-filters .filter-dot { display: block; }

    .filter-panel { display: block; margin-top: 0; padding: 14px 16px;
        background: var(--bg-surface);
        border: 1px solid var(--border); border-radius: 12px;
        box-shadow: var(--shadow);
    }
    .filter-panel-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
    .filter-panel-title {
        font-size: 12px; font-weight: 700; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.08em;
    }
    .clear-filters-btn {
        border: 1px solid var(--border); background: var(--bg-surface);
        color: var(--text-muted); border-radius: 8px; padding: 4px 10px;
        font-size: 12px; font-weight: 600; font-family: var(--font-body);
        cursor: pointer; transition: all 0.15s;
    }
    .clear-filters-btn:hover {
        color: var(--text-main); border-color: var(--text-muted); background: var(--bg-muted);
    }
    .simple-filter-row { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
    .simple-filter-row:last-child { margin-bottom: 0; }
    .filter-date-input, .filter-select {
        width: 100%;
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: var(--bg-surface);
        color: var(--text-main);
        font-size: 13px;
        font-family: var(--font-body);
        outline: none;
    }
    .filter-date-input:focus, .filter-select:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent-light);
    }
    .keyword-add-row { display: flex; gap: 8px; }
    .keyword-input {
        flex: 1;
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: var(--bg-surface);
        color: var(--text-main);
        font-size: 13px;
        font-family: var(--font-body);
        outline: none;
    }
    .keyword-input:focus { border-color: var(--accent); }
    .keyword-add-btn {
        border: 1px solid var(--border);
        background: var(--bg-muted);
        color: var(--text-muted);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        font-family: var(--font-body);
    }
    .keyword-chip-list { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
    .keyword-chip { display: inline-flex; align-items: center; gap: 6px; }
    .keyword-remove {
        border: none; background: transparent; color: #94A3B8; cursor: pointer;
        padding: 0; font-size: 12px; line-height: 1;
    }
    .keyword-tools { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
    .keyword-hint { color: #64748B; font-size: 11px; }
    .keyword-clear-btn {
        border: none; background: transparent; color: #94A3B8; cursor: pointer;
        padding: 0; font-size: 12px; font-family: 'Inter', sans-serif;
    }
    .filter-section { margin-bottom: 12px; padding-top: 10px; border-top: 1px solid var(--border-subtle); }
    .filter-section:last-child { margin-bottom: 0; }
    .filter-section-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .filter-section-toggle {
        display: inline-flex; align-items: center; gap: 8px;
        border: none; background: transparent; color: var(--text-muted);
        padding: 0; cursor: pointer; font-family: var(--font-body);
    }
    .filter-section-toggle:hover .filter-label { color: var(--text-main); }
    .filter-label { font-size: 11px; font-weight: 700; color: var(--text-faint);
        text-transform: uppercase; letter-spacing: 0.08em; }
    .filter-count { font-size: 11px; color: var(--text-faint); text-transform: none; letter-spacing: 0; }
    .filter-chevron { font-size: 11px; color: var(--text-faint); transition: transform 0.15s; }
    .filter-section-body.collapsed .filter-chevron { transform: rotate(-90deg); }
    .filter-search {
        width: 100%; margin: 8px 0 8px; padding: 7px 10px;
        border-radius: 8px; border: 1px solid var(--border);
        background: var(--bg-surface); color: var(--text-main);
        font-size: 12px; font-family: var(--font-body); outline: none;
    }
    .filter-search:focus { border-color: var(--accent); }
    .filter-search::placeholder { color: var(--text-faint); }
    .filter-section-body.collapsed .filter-section-content { display: none; }
    .filter-chip-wrap { display: flex; gap: 6px; flex-wrap: wrap; flex: 1; }
    .chip-hidden { display: none; }
    .filter-more-btn {
        margin-top: 8px; border: none; background: transparent; color: var(--accent);
        font-size: 12px; font-weight: 600; font-family: var(--font-body);
        cursor: pointer; padding: 0;
    }
    .filter-more-btn:hover { color: var(--text-main); }

    .ai-bar { display: flex; flex-direction: column; gap: 10px; }
    .ai-bar-inner { display: flex; align-items: stretch; gap: 0;
        position: relative;
        border-radius: 12px; padding: 12px 14px;
        border: 2px solid transparent;
        background-image:
            linear-gradient(var(--bg-elevated), var(--bg-elevated)),
            linear-gradient(135deg, #6366F1, #8B5CF6, #EC4899);
        background-origin: border-box; background-clip: padding-box, border-box;
        box-shadow: 0 4px 20px rgba(99,102,241,0.12);
        animation: aiExpand 0.2s ease; }
    @keyframes aiExpand {
        from { opacity: 0; transform: scaleY(0.9); }
        to   { opacity: 1; transform: scaleY(1); } }
    .ai-query-input { display: block; width: 100%; border: none; outline: none; background: transparent;
        resize: vertical; height: 192px; min-height: 192px; max-height: 320px;
        padding: 0 0 48px 0;
        font-family: var(--font-body); font-size: 14px; line-height: 1.45;
        color: var(--text-main); }
    .ai-query-input::placeholder { color: #94A3B8; }
    .ai-field-actions {
        position: absolute;
        right: 10px;
        bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .ai-submit-btn {
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: #fff; border: none; border-radius: 10px;
        width: 42px; height: 42px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 700; cursor: pointer;
        font-family: 'Inter', sans-serif; transition: opacity 0.15s; line-height: 1; }
    .ai-submit-btn:hover { opacity: 0.88; }

    .thinking-bar { display: none; align-items: center; gap: 8px;
        padding: 6px 10px;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(139,92,246,0.26); border-radius: 999px; }
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

    .ds-list-box {
        width: 100%; min-width: 0; box-sizing: border-box;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px; overflow: hidden;
        box-shadow: 0 1px 0 var(--border-subtle) inset;
    }
    .ds-count-bar {
        display: flex; align-items: center; justify-content: space-between;
        flex-wrap: wrap; gap: 8px 12px;
        padding: 8px 16px; border-bottom: 1px solid var(--border-subtle);
        font-size: 12px; color: var(--text-muted); background: var(--bg-muted);
    }
    .ds-count-controls { display: flex; align-items: center; gap: 12px; }
    .per-page-wrap { display: flex; align-items: center; gap: 6px; }
    .per-page-label { font-size: 11px; color: var(--text-faint); }
    .per-page-select { font-size: 12px; color: var(--text-muted); background: var(--bg-surface);
        border: 1px solid var(--border); border-radius: 6px; padding: 4px 8px;
        cursor: pointer; font-family: var(--font-body); outline: none; }
    .per-page-select:focus { border-color: var(--accent); }
    .ds-pagination { display: flex; align-items: center; justify-content: center;
        gap: 4px; padding: 12px 16px; border-top: 1px solid var(--border-subtle); }
    .page-btn { display: inline-flex; align-items: center; justify-content: center;
        min-width: 32px; height: 32px; padding: 0 8px; border-radius: 6px;
        font-size: 13px; font-weight: 500; text-decoration: none;
        border: 1px solid var(--border); color: var(--text-muted); background: var(--bg-surface);
        cursor: pointer; transition: all 0.12s; }
    .page-btn:hover { border-color: var(--text-muted); background: var(--bg-muted); color: var(--text-main); }
    .page-btn.active { background: var(--accent); border-color: var(--accent); color: #FFFFFF; font-weight: 600; }
    .page-btn.disabled { color: var(--text-faint); cursor: default; pointer-events: none; border-color: var(--border-subtle); }
    .page-ellipsis { color: var(--text-faint); font-size: 13px; padding: 0 4px; }
    .ds-list { display: flex; flex-direction: column; }
    .ds-row { display: flex; align-items: center; gap: 10px; padding: 11px 14px;
        border-bottom: 1px solid var(--border-subtle); transition: background 0.1s; }
    .ds-row:last-child { border-bottom: none; }
    .ds-row:hover { background: var(--bg-muted); }

    .ds-expand { border-bottom: 1px solid var(--border-subtle); }
    .ds-expand:last-child { border-bottom: none; }
    .ds-expand-summary { list-style: none; cursor: pointer; padding: 0; }
    .ds-expand-summary::-webkit-details-marker { display: none; }
    .ds-expand-summary::marker { display: none; }
    .ds-row-inner { display: flex; align-items: center; gap: 10px; padding: 11px 14px;
        transition: background 0.1s; }
    .ds-expand-summary:hover .ds-row-inner,
    .ds-expand[open] .ds-row-inner { background: var(--bg-muted); }
    .ds-expand-chevron { color: var(--text-faint); font-size: 11px; flex-shrink: 0; width: 12px;
        transition: transform 0.15s ease; line-height: 1; margin-top: 1px; }
    .ds-expand[open] .ds-expand-chevron { transform: rotate(90deg); color: var(--text-muted); }

    .ds-detail-panel { padding: 0 14px 14px 38px; border-top: 1px solid var(--border-subtle);
        background: var(--bg-muted); }
    .ds-detail-desc { font-size: 13px; color: var(--text-muted); line-height: 1.65; margin-bottom: 12px; }
    .ds-detail-meta-inline { display: flex; flex-wrap: wrap; gap: 10px 16px; font-size: 12px;
        color: var(--text-muted); margin-bottom: 14px; }
    .ds-detail-meta-inline strong { color: var(--text-main); font-weight: 600; }
    .ds-detail-section { font-size: 11px; font-weight: 600; color: var(--text-faint); text-transform: uppercase;
        letter-spacing: 0.06em; margin: 16px 0 8px; }
    .ds-detail-section:first-child { margin-top: 4px; }
    .ds-inline-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }
    .ds-inline-tag { font-size: 11px; font-weight: 600; color: var(--text-muted); background: var(--bg-surface);
        border: 1px solid var(--border); padding: 2px 8px; border-radius: 4px; }
    .ds-inline-table-wrap { overflow-x: auto; border-radius: 8px; border: 1px solid var(--border);
        background: var(--bg-surface); }
    .ds-inline-schema { width: 100%; border-collapse: collapse; font-size: 12px; }
    .ds-inline-schema th { text-align: left; padding: 7px 10px; font-size: 10px; font-weight: 600;
        color: var(--text-faint); text-transform: uppercase; letter-spacing: 0.04em;
        border-bottom: 1px solid var(--border); background: var(--bg-muted); }
    .ds-inline-schema td { padding: 7px 10px; color: var(--text-muted); border-bottom: 1px solid var(--border-subtle);
        vertical-align: top; }
    .ds-inline-schema tr:last-child td { border-bottom: none; }
    .ds-inline-col-name { font-family: var(--font-mono); font-size: 11px; color: var(--text-main); font-weight: 500; }
    .ds-inline-col-type { font-family: var(--font-mono); font-size: 10px; color: var(--accent);
        background: var(--accent-light); padding: 1px 6px; border-radius: 4px; font-weight: 600; }
    .ds-inline-col-desc { color: var(--text-muted); font-size: 12px; }
    .ds-inline-sample { width: 100%; border-collapse: collapse; font-size: 11px; }
    .ds-inline-sample th { text-align: left; padding: 6px 10px; font-size: 10px; font-weight: 600;
        color: var(--text-faint); text-transform: uppercase; white-space: nowrap;
        border-bottom: 1px solid var(--border); background: var(--bg-muted); }
    .ds-inline-sample td { padding: 6px 10px; color: var(--text-muted); border-bottom: 1px solid var(--border-subtle);
        font-family: var(--font-mono); white-space: nowrap; }
    .ds-inline-sample tr:last-child td { border-bottom: none; }
    .ds-inline-code { background: var(--bg-muted); border: 1px solid var(--border);
        border-radius: 7px; padding: 10px 12px; font-family: var(--font-mono); font-size: 11px;
        color: var(--text-main); line-height: 1.55; overflow-x: auto; white-space: pre; margin-top: 4px; }
    .ds-inline-muted { font-size: 12px; color: var(--text-faint); }
    .ds-inline-full { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-subtle); }
    .ds-inline-full a { font-size: 12px; color: var(--accent); text-decoration: none; font-weight: 500; }
    .ds-inline-full a:hover { text-decoration: underline; }

    .ds-row-mid { flex: 1; min-width: 0; }
    .ds-name { font-size: 14px; font-weight: 600; color: var(--text-main); text-decoration: none;
        display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; }
    .ds-name:hover { color: var(--accent); }
    .ds-name-btn { cursor: pointer; }
    .ds-expand-summary:hover .ds-name { color: var(--accent); }
    .ds-meta { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
    .ds-cat-label { font-size: 12px; color: var(--text-muted); }
    .ds-sep { color: var(--text-faint); font-size: 12px; }
    .ds-prov { font-size: 12px; color: var(--text-muted); white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis; max-width: 220px; }
    .ds-desc { font-size: 12px; color: var(--text-muted); margin-top: 2px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .ds-row-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
    .badge { padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-freq { background: rgba(148,163,184,0.12); color: #94A3B8; font-weight: 500; border: 1px solid rgba(148,163,184,0.15); }

    .fav-btn { background: transparent; border: none; cursor: pointer;
        font-size: 20px; color: var(--text-faint); padding: 3px 6px; line-height: 1;
        transition: color 0.15s; flex-shrink: 0; }
    .fav-btn:hover { color: #F59E0B; }
    .fav-btn.on { color: #F59E0B; }

    .add-btn {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        color: var(--text-muted); font-size: 12px; font-weight: 600; padding: 4px 11px;
        border-radius: 6px; cursor: pointer; font-family: var(--font-body);
        transition: all 0.15s; white-space: nowrap; flex-shrink: 0; }
    .add-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
    .added-badge { font-size: 12px; font-weight: 600; color: var(--brand-green); padding: 3px 6px;
        white-space: nowrap; }
    .remove-link { background: transparent; border: none; color: var(--text-faint); font-size: 11px;
        cursor: pointer; padding: 0; font-family: var(--font-body); }
    .remove-link:hover { color: var(--brand-error); }

    .ai-reason { font-size: 12px; color: var(--text-muted); margin-top: 3px;
        border-left: 2px solid var(--accent); padding-left: 8px; line-height: 1.5; }
    .ai-banner { background: var(--accent-light);
        border: 1px solid var(--accent);
        border-radius: 8px; padding: 10px 14px; margin-bottom: 14px;
        font-size: 13px; color: var(--accent); }
    .empty-msg { padding: 40px 20px; color: var(--text-muted); font-size: 14px; text-align: center; }

    .cat-fav-select-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        flex-wrap: wrap;
        width: 100%;
        justify-content: flex-end;
    }
    .cat-fav-select-row .cat-fav-select { flex: 1; min-width: 160px; max-width: 280px; }
    .fav-delete-btn {
        background: transparent; border: 1px solid rgba(255,255,255,0.12); color: #94A3B8;
        padding: 8px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
        font-family: var(--font-body); transition: all 0.15s; white-space: nowrap; flex-shrink: 0;
    }
    .fav-delete-btn:hover {
        border-color: rgba(252,165,165,0.4); color: #EF4444; background: rgba(239,68,68,0.08);
    }

    @media (max-width: 1100px) {
        .cat-wrap { flex-wrap: wrap; }
        .cat-sidebar {
            width: 100%;
            position: static;
            top: auto;
            height: auto;
            border-bottom: 1px solid var(--border);
            padding: 16px 20px;
        }
        .cat-results-col {
            width: 100%; border-right: none; padding: 24px 20px 0;
            position: static; top: auto; height: auto; overflow-y: visible;
        }
        .cat-controls-col {
            width: 100%; min-width: 0; padding: 16px 20px 24px;
            position: static; top: auto; height: auto; overflow-y: visible;
        }
        .cat-splitter { display: none; }
    }
""")


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _favourite_lists_rows(user_id):
    if not user_id:
        return []
    try:
        return db_select("favourite_lists", {"user_id": user_id})
    except Exception:
        return []


def _slugs_for_favourite_list(user_id, fav_list_id_str):
    """Return slug list for a list owned by the user, or [] if missing or invalid."""
    if not user_id or not fav_list_id_str:
        return []
    lid = str(fav_list_id_str).strip()
    if not lid:
        return []
    try:
        lst = db_select("favourite_lists", {"id": lid, "user_id": user_id})
    except Exception:
        return []
    if not lst:
        return []
    try:
        items = db_select("favourite_items", {"list_id": lid, "user_id": user_id})
    except Exception:
        return []
    return [row["dataset_slug"] for row in items]


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


def _dataset_inline_detail(d):
    """Expanded panel below a catalog row (same information as the dataset detail page, compact)."""
    slug = d.get("slug") or ""
    schema_fields = d.get("schema_fields") or []
    sample_rows = d.get("sample_rows") or []
    tags = d.get("tags") or []
    table_name = slug.replace("-", "_").upper()
    long_desc = d.get("long_description") or d.get("description") or ""

    meta_bits = [
        Div(Span("Provider: "), Strong(d.get("provider") or "—")),
        Div(Span("Updates: "), Strong(d.get("update_frequency") or "—")),
    ]

    if schema_fields:
        schema_body = Tbody(*[
            Tr(
                Td(Span(f.get("name", ""), cls="ds-inline-col-name")),
                Td(Span(f.get("type", ""), cls="ds-inline-col-type")),
                Td(f.get("description", "") or "", cls="ds-inline-col-desc"),
            )
            for f in schema_fields
        ])
        schema_block = Div(
            Table(
                Thead(Tr(Th("Column"), Th("Type"), Th("Description"))),
                schema_body,
                cls="ds-inline-schema",
            ),
            cls="ds-inline-table-wrap",
        )
    else:
        schema_block = P("Schema not yet documented.", cls="ds-inline-muted")

    if sample_rows and isinstance(sample_rows, list) and len(sample_rows) > 0:
        cols = list(sample_rows[0].keys())[:6]
        sample_block = Div(
            Table(
                Thead(Tr(*[Th(c) for c in cols])),
                Tbody(*[
                    Tr(*[Td(str(row.get(c, "")) if row.get(c) is not None else "null") for c in cols])
                    for row in sample_rows[:8]
                ]),
                cls="ds-inline-sample",
            ),
            cls="ds-inline-table-wrap",
        )
    else:
        sample_block = P("Sample data not available.", cls="ds-inline-muted")

    tags_block = (
        Div(*[Span(f"#{t}", cls="ds-inline-tag") for t in tags], cls="ds-inline-tags")
        if tags
        else None
    )

    return Div(
        P(long_desc, cls="ds-detail-desc") if long_desc else None,
        Div(*meta_bits, cls="ds-detail-meta-inline"),
        tags_block,
        P("Schema", cls="ds-detail-section"),
        schema_block,
        P("Sample rows", cls="ds-detail-section"),
        sample_block,
        P("Query example", cls="ds-detail-section"),
        Div(f"SELECT *\nFROM LONDON_DB.PUBLIC.{table_name}\nLIMIT 100;", cls="ds-inline-code"),
        Div(
            A("Open full page", href=f"/catalog/{slug}"),
            cls="ds-inline-full",
        ),
        cls="ds-detail-panel",
    )


def _list_row(d, is_fav=False, ai_reason=None):
    slug   = d.get("slug", "")
    cat    = d.get("category") or ""
    freq   = FREQ_SHORT.get(d.get("update_frequency") or "", "")

    mid = Div(
        Span(d.get("title") or slug, cls="ds-name ds-name-btn"),
        Div(
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
        _fav_btn(slug, is_fav),
        cls="ds-row-right",
        onclick="event.stopPropagation()",
    )
    return Details(
        Summary(
            Div(
                Span("▸", cls="ds-expand-chevron"),
                mid,
                right,
                cls="ds-row-inner",
            ),
            cls="ds-expand-summary",
        ),
        _dataset_inline_detail(d),
        cls="ds-expand",
    )


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
        hx_include="#catalog-fav-list-select",
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
            var addEl = document.getElementById('add-{slug}');
            if (addEl) htmx.ajax('GET', '/catalog/{slug}/add-btn', {{target: '#add-{slug}', swap: 'outerHTML'}});
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


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar(counts, active_cat, total):
    items = [
        Div("Browse", cls="cat-sidebar-title"),
        A(Span("All datasets", cls="cat-sidebar-label"),
          Span(str(total), cls="cat-sidebar-count"),
          href="/catalog",
          cls=f"cat-sidebar-item {'active' if not active_cat else ''}"),
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
    return Div(*items, cls="cat-sidebar", id="cat-sidebar-col")


# ── Search area ───────────────────────────────────────────────────────────────

def _keyword_search_area(q, category, freq_f="", updated_after_f="", size_f="", keywords_f="", sort_f="recent", fav_list=""):
    search_svg = NotStr('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>')

    kw_bar = Div(
        Div(search_svg, cls="kw-icon"),
        Input(type="search", name="q", value=q,
              placeholder="Search datasets…",
              cls="kw-input",
              hx_get="/catalog/search",
              hx_trigger="input changed delay:280ms, search",
              hx_target="#catalog-body",
              hx_include="[name='q'],[name='category'],[name='freq'],[name='updated_after'],[name='size'],[name='keywords'],[name='sort'],[name='fav_list']",
              hx_push_url="true"),
        Input(type="hidden", name="category", value=category, id="kw-filter-category"),
        Input(type="hidden", name="freq",     value=freq_f, id="kw-filter-freq"),
        Input(type="hidden", name="updated_after", value=updated_after_f, id="kw-filter-updated-after"),
        Input(type="hidden", name="size", value=size_f, id="kw-filter-size"),
        Input(type="hidden", name="keywords", value=keywords_f, id="kw-filter-keywords"),
        Input(type="hidden", name="sort", value=sort_f or "recent", id="kw-filter-sort"),
        Input(type="hidden", name="fav_list", value=fav_list, id="kw-filter-fav-list"),
        id="kw-bar", cls="kw-bar"
    )

    return Div(kw_bar, cls="kw-search-wrap")


def _ai_filter_area(q, category, freq_f="", updated_after_f="", size_f="", keywords_f="", fav_list=""):
    keyword_items = [w.strip() for w in str(keywords_f or "").split(",") if w.strip()][:10]
    controls_slicer = Div(
        Button("AI Search", type="button", id="controls-tab-ai",
               cls="controls-slicer-btn active", onclick="setControlsPanel('ai')"),
        Button("Filters", type="button", id="controls-tab-filters",
               cls="controls-slicer-btn", onclick="setControlsPanel('filters')"),
        cls="controls-slicer"
    )

    ai_bar = Form(
        Input(type="hidden", name="fav_list", value=fav_list, id="ai-fav-list"),
        Div(
            Textarea(
                name="query",
                placeholder="Describe the data you need or the task you are working on (for example: 'Find datasets for KYC and company ownership checks').",
                cls="ai-query-input",
                id="ai-query-input"
            ),
            Div(
                Div(
                    Div(
                        Div(cls="thinking-dot"), Div(cls="thinking-dot"), Div(cls="thinking-dot"),
                        cls="thinking-dots"
                    ),
                    Span("Searching...", id="thinking-msg", cls="thinking-msg"),
                    id="thinking-bar", cls="thinking-bar"
                ),
                Button("↑", type="submit", cls="ai-submit-btn", title="Run AI search"),
                cls="ai-field-actions"
            ),
            cls="ai-bar-inner"
        ),
        hx_post="/catalog/ai-search",
        hx_target="#catalog-body",
        cls="ai-bar", id="ai-bar"
    )

    filter_panel = Div(
        Div(
            Span("Filters", cls="filter-panel-title"),
            Button("Clear filters", type="button", cls="clear-filters-btn", onclick="clearCatalogSimpleFilters()"),
            cls="filter-panel-head"
        ),
        Div(
            Span("Last updated after", cls="filter-label"),
            Input(type="date", value=updated_after_f, id="filter-updated-after", cls="filter-date-input",
                  onchange="setCatalogSimpleFilter('updated_after', this.value)"),
            cls="simple-filter-row"
        ),
        Div(
            Span("Update frequency", cls="filter-label"),
            Select(
                Option("Any frequency", value="", selected=(not freq_f)),
                *[Option(lbl, value=val, selected=(freq_f == val)) for lbl, val in FREQ_FILTERS],
                id="filter-frequency", cls="filter-select",
                onchange="setCatalogSimpleFilter('freq', this.value)"
            ),
            cls="simple-filter-row"
        ),
        Div(
            Span("Dataset size", cls="filter-label"),
            Select(
                Option("Any size", value="", selected=(not size_f)),
                *[Option(lbl, value=val, selected=(size_f == val)) for lbl, val in SIZE_FILTERS],
                id="filter-size", cls="filter-select",
                onchange="setCatalogSimpleFilter('size', this.value)"
            ),
            cls="simple-filter-row"
        ),
        Div(
            Span("Keywords", cls="filter-label"),
            Div(
                Input(type="text", id="filter-keyword-input", cls="keyword-input",
                      placeholder="Type a word and add",
                      onkeydown="if(event.key==='Enter'){event.preventDefault();addCatalogKeyword();}"),
                Button("Add", type="button", cls="keyword-add-btn", onclick="addCatalogKeyword()"),
                cls="keyword-add-row"
            ),
            Div(
                *[
                    Span(
                        Span(w),
                        Button("×", type="button", cls="keyword-remove",
                               onclick=f"removeCatalogKeyword({json.dumps(w)})"),
                        cls="chip keyword-chip"
                    )
                    for w in keyword_items
                ],
                id="keyword-chip-list",
                cls="keyword-chip-list"
            ),
            Div(
                Span("Up to 10 keywords. OR matching.", cls="keyword-hint"),
                Button("Clear all", type="button", cls="keyword-clear-btn", onclick="clearCatalogKeywords()"),
                cls="keyword-tools"
            ),
            cls="simple-filter-row"
        ),
        id="filter-panel",
        cls="filter-panel"
    )

    script = Script("""
        const _thinkMsgs = ['Searching...','Thinking...','Analysing datasets...','Finding matches...','Almost there...'];
        let _thinkIdx = 0, _thinkTimer = null;

        const _catalogFilterInputIds = {
            category: 'kw-filter-category',
            freq: 'kw-filter-freq',
            updated_after: 'kw-filter-updated-after',
            size: 'kw-filter-size',
            keywords: 'kw-filter-keywords',
        };

        function _splitCsv(raw) {
            if (!raw) return [];
            return String(raw).split(',').map(v => v.trim()).filter(Boolean);
        }

        function _currentQuery() {
            const kw = document.querySelector('#kw-bar input[name="q"]');
            return kw ? kw.value : '';
        }

        function _currentPerPage() {
            const pp = document.querySelector('.per-page-select');
            return pp ? pp.value : '25';
        }

        function _currentSort() {
            const sort = document.getElementById('kw-filter-sort');
            return sort ? (sort.value || 'recent') : 'recent';
        }

        function _readFilter(filterName) {
            const id = _catalogFilterInputIds[filterName];
            const el = id ? document.getElementById(id) : null;
            return el ? _splitCsv(el.value) : [];
        }

        function _writeFilter(filterName, values) {
            const id = _catalogFilterInputIds[filterName];
            const el = id ? document.getElementById(id) : null;
            if (el) el.value = values.join(',');
        }

        function _runCatalogFilterSearch() {
            const favEl = document.getElementById('kw-filter-fav-list');
            const params = new URLSearchParams({
                q: _currentQuery(),
                category: (_readFilter('category') || []).join(','),
                freq: (_readFilter('freq') || []).join(','),
                updated_after: (_readFilter('updated_after') || []).join(','),
                size: (_readFilter('size') || []).join(','),
                keywords: (_readFilter('keywords') || []).join(','),
                sort: _currentSort(),
                page: '1',
                per_page: _currentPerPage(),
                fav_list: favEl ? (favEl.value || '') : '',
            });
            const qs = params.toString();
            htmx.ajax('GET', '/catalog/search?' + qs, {
                target: '#catalog-body',
                pushUrl: '/catalog?' + qs
            });
        }
        window._runCatalogFilterSearch = _runCatalogFilterSearch;

        function setCatalogSimpleFilter(filterName, value) {
            _writeFilter(filterName, value ? [value] : []);
            _runCatalogFilterSearch();
        }

        function _readKeywords() {
            return (_readFilter('keywords') || []).slice(0, 10);
        }

        function _renderKeywordChips() {
            const list = document.getElementById('keyword-chip-list');
            if (!list) return;
            const words = _readKeywords();
            list.innerHTML = '';
            words.forEach(function(w) {
                const chip = document.createElement('span');
                chip.className = 'chip keyword-chip';
                const text = document.createElement('span');
                text.textContent = w;
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'keyword-remove';
                btn.textContent = '×';
                btn.addEventListener('click', function() { removeCatalogKeyword(w); });
                chip.appendChild(text);
                chip.appendChild(btn);
                list.appendChild(chip);
            });
        }

        function addCatalogKeyword() {
            const input = document.getElementById('filter-keyword-input');
            if (!input) return;
            const word = (input.value || '').trim();
            if (!word) return;
            const words = _readKeywords();
            const lower = words.map(function(w) { return w.toLowerCase(); });
            if (lower.includes(word.toLowerCase())) {
                input.value = '';
                return;
            }
            if (words.length >= 10) return;
            words.push(word);
            _writeFilter('keywords', words);
            input.value = '';
            _renderKeywordChips();
            _runCatalogFilterSearch();
        }

        function removeCatalogKeyword(word) {
            const words = _readKeywords().filter(function(w) { return w !== word; });
            _writeFilter('keywords', words);
            _renderKeywordChips();
            _runCatalogFilterSearch();
        }

        function clearCatalogKeywords() {
            _writeFilter('keywords', []);
            _renderKeywordChips();
            _runCatalogFilterSearch();
        }

        function clearCatalogSimpleFilters() {
            Object.keys(_catalogFilterInputIds).forEach(function(k) { _writeFilter(k, []); });
            const d = document.getElementById('filter-updated-after');
            const f = document.getElementById('filter-frequency');
            const s = document.getElementById('filter-size');
            const k = document.getElementById('filter-keyword-input');
            if (d) d.value = '';
            if (f) f.value = '';
            if (s) s.value = '';
            if (k) k.value = '';
            _renderKeywordChips();
            _runCatalogFilterSearch();
        }

        function setControlsPanel(panel) {
            const aiTab = document.getElementById('controls-tab-ai');
            const filterTab = document.getElementById('controls-tab-filters');
            const aiPanel = document.getElementById('controls-panel-ai');
            const filterPanel = document.getElementById('controls-panel-filters');
            if (!aiTab || !filterTab || !aiPanel || !filterPanel) return;

            const isAi = panel === 'ai';
            aiTab.classList.toggle('active', isAi);
            filterTab.classList.toggle('active', !isAi);
            aiPanel.classList.toggle('active', isAi);
            filterPanel.classList.toggle('active', !isAi);
        }

        function activateAI() { setControlsPanel('ai'); }
        function deactivateAI() {}
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
        _renderKeywordChips();
    """)

    return Div(
        controls_slicer,
        Div(
            Div(
                ai_bar,
                id="controls-panel-ai",
                cls="controls-panel active"
            ),
            Div(
                filter_panel,
                id="controls-panel-filters",
                cls="controls-panel"
            )
        ),
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


def _fav_list_dropdown(fav_list, fav_rows, user_id, oob=False):
    if not user_id:
        return None
    opts = [Option("All datasets", value="", selected=(not fav_list))]
    for row in fav_rows:
        lid = str(row["id"])
        opts.append(Option(row.get("name") or "List", value=lid, selected=(str(fav_list) == lid)))
    sel = Select(
        *opts,
        id="catalog-fav-list-select",
        cls="cat-fav-select",
        name="fav_list",
        hx_get="/catalog/search",
        hx_trigger="change",
        hx_target="#catalog-body",
        hx_push_url="true",
        hx_include="#kw-bar input, #ai-bar input",
        onchange=(
            "var v=this.value;"
            "var h=document.getElementById('kw-filter-fav-list'); if(h) h.value=v;"
            "var ai=document.getElementById('ai-fav-list'); if(ai) ai.value=v;"
        ),
    )
    delete_form = None
    trash_svg = NotStr('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:block;"><path d="M3 6h18m-2 0v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>')
    if fav_list:
        delete_form = Form(
            Button(trash_svg, type="submit", cls="fav-delete-btn", title="Delete this favourite list"),
            method="post",
            action=f"/favourite-lists/{fav_list}/delete",
            onsubmit="return confirm('Delete this favourite list? Dataset entries are removed from the list only.');",
        )
    control_row = Div(sel, delete_form, cls="cat-fav-select-row") if delete_form else sel
    
    attrs = {"hx_swap_oob": "true"} if oob else {}
    return Div(
        Span("Show Favourite", cls="cat-fav-select-label"),
        control_row,
        id="fav-list-dropdown-container",
        cls="cat-fav-select-wrap",
        **attrs
    )


def _list_body(page_datasets, total, favs, heading, subtext, page=1, per_page=25,
               q="", category="", freq_f="", updated_after_f="", size_f="", keywords_f="", sort_f="recent",
               fav_list="", fav_rows=None, user_id=""):
    fav_rows = fav_rows or []
    fav_dropdown = _fav_list_dropdown(fav_list, fav_rows, user_id)

    def header_block():
        inner_title = Div(
            H1(heading, style="font-size:18px;font-weight:600;color:var(--text-main);letter-spacing:-0.03em;"),
            P(subtext, style="font-size:13px;color:var(--text-muted);margin-top:3px;"),
            cls="cat-header-text",
        )
        if fav_dropdown:
            return Div(inner_title, fav_dropdown, cls="cat-header-row")
        return Div(
            H1(heading, style="font-size:18px;font-weight:600;color:var(--text-main);letter-spacing:-0.03em;"),
            P(subtext, style="font-size:13px;color:var(--text-muted);margin-top:3px;"),
            style="margin-bottom:14px;",
        )

    fav_q = f"&fav_list={fav_list}" if fav_list else ""

    if not page_datasets:
        return Div(
            header_block(),
            Div(P("No datasets match.", cls="empty-msg"), cls="ds-list-box"),
        )

    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    qs_base_no_sort = (
        f"q={q}&category={category}&freq={freq_f}"
        f"&updated_after={updated_after_f}&size={size_f}&keywords={keywords_f}{fav_q}"
    )
    qs_base = f"{qs_base_no_sort}&sort={sort_f or 'recent'}"

    per_page_select = Select(
        *[Option(str(n), value=str(n), selected=(n == per_page)) for n in [25, 50, 100, 200]],
        cls="per-page-select",
        onchange=f"htmx.ajax('GET', '/catalog/search?{qs_base}&page=1&per_page=' + this.value, "
                 f"{{target:'#catalog-body', pushUrl:'/catalog?{qs_base}&page=1&per_page=' + this.value}})"
    )
    sort_select = Select(
        *[Option(lbl, value=val, selected=((sort_f or "recent") == val)) for lbl, val in SORT_OPTIONS],
        cls="per-page-select",
        onchange=(
            "var hidden=document.getElementById('kw-filter-sort');"
            "if(hidden){hidden.value=this.value;}"
            f"htmx.ajax('GET', '/catalog/search?{qs_base_no_sort}&sort=' + encodeURIComponent(this.value) + '&page=1&per_page={per_page}', "
            f"{{target:'#catalog-body', pushUrl:'/catalog?{qs_base_no_sort}&sort=' + encodeURIComponent(this.value) + '&page=1&per_page={per_page}'}})"
        )
    )

    count_bar = Div(
        Span(f"{total} dataset{'s' if total != 1 else ''}"),
        Div(
            Div(Span("Sort", cls="per-page-label"), sort_select, cls="per-page-wrap"),
            Div(Span("View", cls="per-page-label"), per_page_select, cls="per-page-wrap"),
            cls="ds-count-controls"
        ),
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
        header_block(),
        Div(
            count_bar,
            Div(*[_list_row(d, is_fav=d.get("slug") in favs)
                  for d in page_datasets], cls="ds-list"),
            Div(*page_items, cls="ds-pagination") if total_pages > 1 else None,
            cls="ds-list-box"
        )
    )


# ── Public components ─────────────────────────────────────────────────────────

def DataCatalog(category="", q="", user_id="", freq_filter="", updated_after_filter="", size_filter="", keywords_filter="", sort_filter="recent", page=1, per_page=25, fav_list=""):
    from app.supabase_db import get_datasets_paginated, get_category_counts
    effective_fav = fav_list if user_id else ""
    fav_rows = _favourite_lists_rows(user_id)
    slug_in = None
    if effective_fav:
        slug_in = _slugs_for_favourite_list(user_id, effective_fav)

    try:
        datasets, total_matches = get_datasets_paginated(
            category, q, "", freq_filter, page, per_page,
            updated_after=updated_after_filter, size=size_filter, keywords=keywords_filter, sort=sort_filter,
            slug_in=slug_in if effective_fav else None,
        )
        counts, total_all = get_category_counts()
    except Exception:
        datasets, counts, total_matches, total_all = [], {}, 0, 0

    _, favs = _fetch_user_sets(user_id)

    fav_list_name = ""
    if effective_fav:
        for row in fav_rows:
            if str(row["id"]) == str(effective_fav):
                fav_list_name = row.get("name") or ""
                break

    if q:
        heading = f'Results for "{q}"'
    elif category:
        heading = category
    elif fav_list_name:
        heading = fav_list_name
    else:
        heading = "London Database"

    has_filters = any([category, freq_filter, updated_after_filter, size_filter, keywords_filter, effective_fav])
    subtext = (f"{total_matches} dataset{'s' if total_matches != 1 else ''} found"
               if (q or has_filters)
               else f"{total_matches} datasets — growing continuously")

    resize_script = Script("""
        (function () {
            const minDesktop = window.matchMedia("(min-width: 1101px)");
            const defaultSidebar = 240;
            const defaultControls = 340;
            const sidebar = document.getElementById("cat-sidebar-col");
            const controls = document.getElementById("cat-controls-col");
            const leftHandle = document.getElementById("cat-splitter-left");
            const rightHandle = document.getElementById("cat-splitter-right");
            if (!sidebar || !controls || !leftHandle || !rightHandle) return;

            const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));

            function loadSavedWidths() {
                if (!minDesktop.matches) {
                    sidebar.style.width = "";
                    controls.style.width = "";
                    return;
                }
                const sw = parseInt(localStorage.getItem("catalog.sidebar.width") || "", 10);
                const cw = parseInt(localStorage.getItem("catalog.controls.width") || "", 10);
                if (Number.isFinite(sw)) sidebar.style.width = clamp(sw, 180, 840) + "px";
                if (Number.isFinite(cw)) controls.style.width = clamp(cw, 260, 560) + "px";
            }

            function resetWidths() {
                sidebar.style.width = defaultSidebar + "px";
                controls.style.width = defaultControls + "px";
                localStorage.removeItem("catalog.sidebar.width");
                localStorage.removeItem("catalog.controls.width");
            }

            function attachDrag(handle, target, key, minW, maxW, sign) {
                let startX = 0;
                let startW = 0;

                function onMove(e) {
                    const delta = e.clientX - startX;
                    const next = clamp(startW + delta * sign, minW, maxW);
                    target.style.width = next + "px";
                }

                function onUp() {
                    handle.classList.remove("dragging");
                    document.body.style.userSelect = "";
                    document.body.style.cursor = "";
                    localStorage.setItem(key, parseInt(target.style.width, 10));
                    window.removeEventListener("mousemove", onMove);
                    window.removeEventListener("mouseup", onUp);
                }

                handle.addEventListener("mousedown", function (e) {
                    if (!minDesktop.matches) return;
                    e.preventDefault();
                    startX = e.clientX;
                    startW = target.getBoundingClientRect().width;
                    handle.classList.add("dragging");
                    document.body.style.userSelect = "none";
                    document.body.style.cursor = "col-resize";
                    window.addEventListener("mousemove", onMove);
                    window.addEventListener("mouseup", onUp);
                });
            }

            loadSavedWidths();
            attachDrag(leftHandle, sidebar, "catalog.sidebar.width", 180, 840, 1);
            attachDrag(rightHandle, controls, "catalog.controls.width", 180, 840, -1);
            leftHandle.addEventListener("dblclick", resetWidths);
            rightHandle.addEventListener("dblclick", resetWidths);
            window.addEventListener("resize", loadSavedWidths);
        })();
    """)

    return Div(
        CATALOG_STYLE,
        Div(
            _sidebar(counts, category, total_all),
            Div(cls="cat-splitter", id="cat-splitter-left", title="Drag to resize columns (double-click to reset)"),
            Div(
                _keyword_search_area(q, category, freq_filter, updated_after_filter, size_filter, keywords_filter, sort_filter, fav_list=effective_fav),
                Div(
                    _list_body(datasets, total_matches, favs, heading, subtext,
                               page=page, per_page=per_page,
                               q=q, category=category, freq_f=freq_filter,
                               updated_after_f=updated_after_filter, size_f=size_filter, keywords_f=keywords_filter,
                               sort_f=sort_filter,
                               fav_list=effective_fav, fav_rows=fav_rows, user_id=user_id),
                    id="catalog-body", cls="cat-main"
                ),
                cls="cat-results-col"
            ),
            Div(cls="cat-splitter", id="cat-splitter-right", title="Drag to resize columns (double-click to reset)"),
            Div(
                _ai_filter_area(q, category, freq_filter, updated_after_filter, size_filter, keywords_filter, fav_list=effective_fav),
                cls="cat-controls-col", id="cat-controls-col"
            ),
            cls="cat-wrap"
        ),
        resize_script
    )


def SearchCatalogResults(q="", category="", user_id="", freq_filter="", updated_after_filter="", size_filter="", keywords_filter="", sort_filter="recent", page=1, per_page=25, fav_list=""):
    from app.supabase_db import get_datasets_paginated
    effective_fav = fav_list if user_id else ""
    fav_rows = _favourite_lists_rows(user_id)
    slug_in = None
    if effective_fav:
        slug_in = _slugs_for_favourite_list(user_id, effective_fav)

    try:
        datasets, total_matches = get_datasets_paginated(
            category, q, "", freq_filter, page, per_page,
            updated_after=updated_after_filter, size=size_filter, keywords=keywords_filter, sort=sort_filter,
            slug_in=slug_in if effective_fav else None,
        )
    except Exception:
        datasets, total_matches = [], 0

    _, favs = _fetch_user_sets(user_id)

    fav_list_name = ""
    if effective_fav:
        for row in fav_rows:
            if str(row["id"]) == str(effective_fav):
                fav_list_name = row.get("name") or ""
                break

    if q:
        heading = f'Results for "{q}"'
    elif category:
        heading = category
    elif fav_list_name:
        heading = fav_list_name
    else:
        heading = "London Database"

    has_filters = any([category, freq_filter, updated_after_filter, size_filter, keywords_filter, effective_fav])
    subtext = (f"{total_matches} dataset{'s' if total_matches != 1 else ''} found"
               if (q or has_filters)
               else f"{total_matches} datasets — growing continuously")
    return _list_body(datasets, total_matches, favs, heading, subtext,
                      page=page, per_page=per_page,
                      q=q, category=category, freq_f=freq_filter,
                      updated_after_f=updated_after_filter, size_f=size_filter, keywords_f=keywords_filter,
                      sort_f=sort_filter,
                      fav_list=effective_fav, fav_rows=fav_rows, user_id=user_id)


def AiSearchResults(query="", user_id="", fav_list=""):
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

    effective_fav = fav_list if user_id else ""
    if effective_fav:
        allow = set(_slugs_for_favourite_list(user_id, effective_fav))
        all_datasets = [d for d in all_datasets if d.get("slug") in allow]

    if not all_datasets:
        return Div(
            P("No datasets in this list to search.", style="color:#64748B;font-size:13px;padding:20px 0;"),
        )

    _, favs = _fetch_user_sets(user_id)

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
                            is_fav=d.get("slug") in favs,
                            ai_reason=slug_to_reason.get(d.get("slug"), ""))
                  for d in ordered], cls="ds-list"),
            cls="ds-list-box"
        )
    )
