"""
All CSS styles for the ODL application.

- get_app_style()          – dark app shell (authenticated pages)
- get_shared_style()       – light marketing / content pages
- get_content_page_style() – inner content layout for light pages
"""
from fasthtml.common import Style


def get_graph_style():
    """CSS for the Companies Graph page — canvas, panels, sidebar, enrichment, intel, status."""
    return Style("""
        /* ── Graph CSS variable bridge: alliela tokens → ODL theme ── */
        :root {
            --bg: var(--bg-page);
            --bg-subtle: var(--bg-muted);
            --bg-card: var(--bg-surface);
            --bg-hover: var(--bg-muted);
            --text: var(--text-main);
            --text-faint: var(--text-faint);
            --border-strong: rgba(255,255,255,0.14);
            --radius: 12px;
            --radius-sm: 8px;
            --font-sans: var(--font-body);
            --text-xs: 10px;
            --text-sm: 12px;
            --text-base: 14px;
            --text-xl: 22px;
            --font-weight-normal: 400;
            --font-weight-medium: 500;
            --font-weight-semibold: 600;
            --font-weight-bold: 700;
            --duration-fast: 100ms;
            --ring: rgba(99,102,241,0.28);
            --accent-muted: rgba(99,102,241,0.15);
            --grid-bg:
                radial-gradient(at 100% 0%, rgba(99,102,241,0.07) 0px, transparent 50%),
                linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
            --grid-size: 100% 100%, 32px 32px, 32px 32px;
        }
        html[data-theme="light"] {
            --bg: #fafafa;
            --bg-subtle: #f4f4f5;
            --bg-card: #ffffff;
            --bg-hover: #f1f5f9;
            --text: #0a0f1a;
            --border-strong: rgba(15,23,42,0.14);
            --ring: rgba(79,70,229,0.28);
            --accent-muted: rgba(79,70,229,0.12);
            --grid-bg:
                radial-gradient(at 100% 0%, rgba(79,70,229,0.05) 0px, transparent 50%),
                linear-gradient(rgba(0,0,0,0.07) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,0,0,0.07) 1px, transparent 1px);
        }

        /* ── Node/edge color tokens (read by JS via getComputedStyle) ── */
        :root {
            --node-company: #4d8eff;
            --node-company-dissolved: #3d4451;
            --node-company-border-dissolved: #4b5263;
            --node-person: #ff7b74;
            --node-person-risk-high: #f87171;
            --node-person-risk-medium: #fbbf24;
            --node-person-risk-low: #4ade80;
            --node-hub-border: #a78bfa;
            --edge-line: rgba(200,210,230,0.15);
            --edge-arrow: rgba(200,210,230,0.22);
            --edge-label-bg: #1c2230;
            --edge-label-color: rgba(139,148,158,0.9);
            --edge-highlighted: #4d8eff;
            --node-selected-border: #e6edf3;
            --graph-bg: #0d1117;
        }
        html[data-theme="light"] {
            --node-company: #0057ff;
            --node-company-dissolved: #94a3b8;
            --node-company-border-dissolved: #64748b;
            --node-person: #ff6961;
            --node-person-risk-high: #dc2626;
            --node-person-risk-medium: #f59e0b;
            --node-person-risk-low: #16a34a;
            --node-hub-border: #7c3aed;
            --edge-line: rgba(15,23,42,0.18);
            --edge-arrow: rgba(15,23,42,0.25);
            --edge-label-bg: #fafafa;
            --edge-label-color: rgba(82,88,102,0.85);
            --edge-highlighted: #0057ff;
            --node-selected-border: #0a0f1a;
            --graph-bg: #fafafa;
        }

        /* ── Graph page layout ── */
        .graph-page {
            flex: 1;
            position: relative;
            overflow: hidden;
            min-height: 0;
        }
        .graph-canvas {
            position: absolute;
            inset: 0;
            background-color: var(--bg);
            background-image: var(--grid-bg);
            background-size: var(--grid-size);
        }

        /* ── Left panel ── */
        .graph-left-panel {
            position: absolute;
            top: 80px;
            left: 16px;
            width: 260px;
            min-width: 200px;
            max-width: 520px;
            max-height: calc(100vh - 80px - 20px - 48px);
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: 0 4px 20px rgba(2,6,23,0.09), 0 1px 4px rgba(2,6,23,0.05);
            z-index: 10;
            display: flex;
            flex-direction: column;
            overflow: visible;
        }
        .graph-left-panel__resize-handle {
            position: absolute;
            top: 0; right: -5px;
            width: 10px; height: 100%;
            cursor: col-resize;
            z-index: 20;
        }
        .graph-left-panel__resize-handle:hover,
        .graph-left-panel__resize-handle--dragging {
            background: rgba(99,102,241,0.25);
        }
        .graph-panel__section {
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .graph-panel__hint {
            font-size: var(--text-xs);
            color: var(--accent);
            font-style: italic;
            font-family: var(--font-sans);
            line-height: 1.4;
        }

        /* ── Search ── */
        .graph-search__form { display: flex; flex-direction: column; gap: 6px; }
        .graph-search__input {
            width: 100%;
            padding: 7px 10px;
            font-family: var(--font-sans);
            font-size: var(--text-sm);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-sm);
            background: var(--bg);
            color: var(--text);
            outline: none;
            transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
        }
        .graph-search__input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--ring);
        }
        .graph-search__btn {
            padding: 7px 12px;
            font-size: var(--text-sm);
            font-weight: var(--font-weight-semibold);
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: opacity var(--duration-fast);
            font-family: var(--font-sans);
        }
        .graph-search__btn:hover { opacity: 0.88; }
        .graph-search__btn:disabled { opacity: 0.45; cursor: not-allowed; }
        .graph-search__btn--add { background: #16a34a; }
        .graph-search__btn--add:disabled { opacity: 0.35; cursor: not-allowed; }
        .graph-search__btn--clear {
            background: transparent;
            color: var(--text-muted);
            border: 1px solid var(--border);
        }
        .graph-search__btn--clear:hover { opacity: 1; color: var(--text); border-color: var(--text); }

        /* ── Search results ── */
        .graph-panel__section--results {
            padding: 0;
            overflow-y: auto;
            max-height: calc(100vh - 80px - 20px - 48px - 120px);
            flex-shrink: 1;
        }
        .search-results__header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 14px 4px;
            flex-shrink: 0;
        }
        .search-results__count {
            font-size: var(--text-xs);
            font-weight: var(--font-weight-semibold);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-muted);
            font-family: var(--font-sans);
        }
        .search-results__clear {
            font-size: var(--text-xs);
            color: var(--accent);
            text-decoration: none;
            font-family: var(--font-sans);
        }
        .search-results__clear:hover { text-decoration: underline; }
        .search-results__items { display: flex; flex-direction: column; }
        .search-result__item {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding: 8px 14px;
            cursor: pointer;
            border-bottom: 1px solid var(--border);
            transition: background var(--duration-fast);
            user-select: none;
        }
        .search-result__item:last-child { border-bottom: none; }
        .search-result__item:hover { background: var(--bg-hover); }
        .search-result__item--selected { background: rgba(99,102,241,0.1); }
        .search-result__item--selected:hover { background: rgba(99,102,241,0.18); }
        .search-result__check-wrap { flex-shrink: 0; margin-top: 2px; }
        .search-result__check-box {
            display: block;
            width: 14px; height: 14px;
            border: 1.5px solid var(--border-strong);
            border-radius: 3px;
            background: var(--bg);
            transition: background var(--duration-fast), border-color var(--duration-fast);
        }
        .search-result__item--selected .search-result__check-box {
            background: var(--accent);
            border-color: var(--accent);
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 10 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 4l3 3 5-6' stroke='%23fff' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
            background-size: 10px 8px;
            background-repeat: no-repeat;
            background-position: center;
        }
        .search-result__body { flex: 1; min-width: 0; overflow: hidden; }
        .search-result__name {
            display: block;
            font-size: var(--text-sm);
            font-weight: var(--font-weight-semibold);
            color: var(--text);
            font-family: var(--font-sans);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        }
        .search-result__row2 {
            display: flex;
            align-items: center;
            gap: 4px;
            margin-top: 2px;
            min-width: 0;
            overflow: hidden;
        }
        .search-result__badge {
            font-size: var(--text-xs);
            font-weight: var(--font-weight-bold);
            padding: 1px 4px;
            border-radius: 3px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            flex-shrink: 0;
        }
        .search-result__badge--company { background: #dbeafe; color: #1d4ed8; }
        .search-result__badge--person  { background: #fce7f3; color: #9d174d; }
        .search-result__badge--disqualified { background: #fee2e2; color: #991b1b; }
        .search-result__status {
            font-size: var(--text-xs);
            font-family: var(--font-sans);
            color: var(--text-muted);
            flex-shrink: 0;
        }
        .search-result__status--active   { color: #16a34a; }
        .search-result__status--dissolved { color: var(--text-muted); }
        .search-result__status--disqualified { color: #dc2626; }
        .search-result__meta {
            font-size: var(--text-xs);
            color: var(--text-muted);
            font-family: var(--font-sans);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            min-width: 0;
        }

        /* ── Spinner ── */
        .graph-spinner {
            width: 14px; height: 14px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: graph-spin 0.7s linear infinite;
            display: none;
            flex-shrink: 0;
            align-self: center;
        }
        .graph-spinner.htmx-request { display: block; }
        @keyframes graph-spin { to { transform: rotate(360deg); } }

        /* ── Sidebar ── */
        .graph-sidebar {
            position: absolute;
            top: 80px; right: 16px;
            width: 260px;
            min-width: 200px;
            max-height: calc(100% - 96px);
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: 0 4px 20px rgba(2,6,23,0.09), 0 1px 4px rgba(2,6,23,0.05);
            overflow-y: auto;
            padding: 16px;
            z-index: 10;
        }
        .graph-sidebar__resize-handle {
            position: absolute;
            top: 0; left: -5px;
            width: 10px; height: 100%;
            cursor: col-resize;
            z-index: 20;
        }
        .graph-sidebar__resize-handle:hover,
        .graph-sidebar__resize-handle--dragging { background: rgba(99,102,241,0.25); }
        .graph-sidebar__placeholder {
            font-size: var(--text-sm);
            color: var(--text-muted);
            text-align: center;
            padding-top: 40px;
            font-family: var(--font-sans);
        }
        .graph-sidebar__name {
            font-size: var(--text-base);
            font-weight: var(--font-weight-bold);
            color: var(--text);
            margin-bottom: 6px;
            line-height: 1.4;
            word-break: break-word;
        }
        .graph-sidebar__badge {
            display: inline-block;
            font-size: var(--text-xs);
            font-weight: var(--font-weight-semibold);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 14px;
            font-family: var(--font-sans);
        }
        .graph-sidebar__badge--company { background: var(--accent-muted); color: var(--accent); }
        .graph-sidebar__badge--person  { background: rgba(255,105,97,0.12); color: #c0392b; }
        .graph-sidebar__table {
            width: 100%;
            border-collapse: collapse;
            font-size: var(--text-sm);
            margin-bottom: 16px;
        }
        .graph-sidebar__th {
            text-align: left;
            padding: 4px 8px 4px 0;
            color: var(--text-muted);
            font-weight: 500;
            width: 44%;
            vertical-align: top;
            font-family: var(--font-sans);
        }
        .graph-sidebar__td {
            text-align: left;
            padding: 4px 0;
            color: var(--text);
            word-break: break-word;
            font-family: var(--font-sans);
        }
        .graph-sidebar__expand-btn {
            display: block;
            width: 100%;
            padding: 9px;
            font-size: var(--text-sm);
            font-weight: var(--font-weight-semibold);
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: opacity var(--duration-fast);
            font-family: var(--font-sans);
            text-align: center;
        }
        .graph-sidebar__expand-btn:hover { opacity: 0.88; }
        .graph-sidebar__detail { display: flex; flex-direction: column; }
        .graph-sidebar__expand-section {
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .graph-sidebar__enrich-btn {
            display: block;
            width: 100%;
            padding: 9px;
            background: #7c3aed;
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: var(--text-sm);
            font-family: var(--font-sans);
            text-align: center;
        }
        .graph-sidebar__enrich-btn:hover { opacity: 0.88; }
        .graph-sidebar__enrich-btn:disabled { opacity: 0.5; cursor: default; }

        /* ── Bottom nav bar ── */
        .graph-bottom-bar {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 4px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 32px;
            box-shadow: 0 4px 20px rgba(2,6,23,0.10), 0 1px 4px rgba(2,6,23,0.06);
            padding: 6px 12px;
            z-index: 10;
        }
        .graph-nav__btn {
            padding: 5px 13px;
            font-size: var(--text-sm);
            font-weight: var(--font-weight-semibold);
            font-family: var(--font-sans);
            background: transparent;
            border: 1px solid transparent;
            border-radius: 20px;
            color: var(--text);
            cursor: pointer;
            transition: background var(--duration-fast), color var(--duration-fast);
            line-height: 1;
        }
        .graph-nav__btn:hover { background: var(--accent-muted); color: var(--accent); }
        .graph-nav__btn--active { background: var(--accent-muted); color: var(--accent); border-color: var(--accent); }
        .graph-nav__btn--active:hover { background: var(--accent); color: #fff; }
        .graph-nav__btn--danger { color: #dc2626; }
        .graph-nav__btn--danger:hover { background: #fee2e2; color: #dc2626; }
        .graph-nav__path-hint {
            font-size: var(--text-xs);
            color: var(--accent);
            font-family: var(--font-sans);
            font-style: italic;
            white-space: nowrap;
        }
        .graph-nav__divider {
            width: 1px; height: 20px;
            background: var(--border);
            margin: 0 6px;
            flex-shrink: 0;
        }
        .graph-nav__depth-group { display: flex; align-items: center; gap: 8px; padding: 0 4px; }
        .graph-nav__depth-label {
            font-size: var(--text-xs);
            font-weight: var(--font-weight-semibold);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-family: var(--font-sans);
            user-select: none;
        }
        .graph-nav__slider { width: 60px; accent-color: var(--accent); cursor: pointer; }
        .graph-nav__depth-val {
            font-family: var(--font-mono);
            font-size: var(--text-sm);
            font-weight: var(--font-weight-semibold);
            color: var(--accent);
            min-width: 10px;
        }
        .graph-nav__color-group { display: flex; flex-direction: column; align-items: center; gap: 2px; }
        .graph-nav__color-label {
            font-size: var(--text-xs);
            font-weight: var(--font-weight-semibold);
            color: var(--text-muted);
            font-family: var(--font-sans);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            line-height: 1;
        }
        .graph-nav__color { width: 26px; height: 18px; padding: 0; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; background: none; }
        .graph-nav__dropdown { position: relative; }
        .graph-nav__dropdown-menu {
            display: none;
            position: absolute;
            bottom: calc(100% + 10px);
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(2,6,23,0.12), 0 1px 4px rgba(2,6,23,0.08);
            padding: 6px 4px;
            min-width: 180px;
            z-index: 20;
            flex-direction: column;
        }
        .graph-nav__dropdown-menu--open { display: flex; }
        .graph-nav__dropdown-item {
            display: flex;
            align-items: center;
            gap: 7px;
            padding: 5px 12px;
            font-size: var(--text-sm);
            font-weight: var(--font-weight-medium);
            color: var(--text);
            cursor: pointer;
            border-radius: 8px;
            white-space: nowrap;
            user-select: none;
        }
        .graph-nav__dropdown-item:hover { background: var(--accent-muted); color: var(--accent); }
        .graph-nav__dropdown-item input[type="checkbox"] { accent-color: var(--accent); width: 14px; height: 14px; cursor: pointer; flex-shrink: 0; }

        /* ── Enrichment panel ── */
        .enrichment-panel { margin-top: 12px; border-top: 1px solid var(--border); padding-top: 10px; }
        .enrichment-panel--loading { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 0; }
        .enrichment-panel--error { color: #991b1b; font-size: var(--text-sm); }
        .enrich-spinner { width: 24px; height: 24px; border: 3px solid var(--border); border-top-color: #7c3aed; border-radius: 50%; animation: spin 0.8s linear infinite; }
        .enrich-spinner__label { font-size: var(--text-xs); color: var(--text-muted); }
        .enrich-tab__list { display: flex; list-style: none; padding: 0; margin: 0 0 8px 0; gap: 2px; flex-wrap: wrap; }
        .enrich-tab__item { margin: 0; }
        .enrich-tab__btn { padding: 4px 8px; font-size: var(--text-xs); font-family: var(--font-sans); background: transparent; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; color: var(--text-muted); }
        .enrich-tab__btn--active { background: #7c3aed; color: #fff; border-color: #7c3aed; }
        .enrich-tab__btn:hover:not(.enrich-tab__btn--active) { background: var(--bg-subtle); }
        .enrich-tab__pane { display: none; }
        .enrich-tab__pane--active { display: block; }
        .enrich-table { font-size: var(--text-xs); width: 100%; }
        .enrich-empty { font-size: var(--text-xs); color: var(--text-muted); padding: 8px 0; }
        .enrich-ch-link { font-size: var(--text-xs); color: #2563eb; text-decoration: none; display: inline-block; margin-top: 8px; }
        .enrich-ch-link:hover { text-decoration: underline; }
        .enrich-error { font-size: var(--text-sm); color: #991b1b; }
        .enrich-badge { font-size: var(--text-xs); padding: 1px 5px; border-radius: 3px; }
        .enrich-badge--active { background: #d1fae5; color: #065f46; }
        .enrich-badge--resigned { background: #fee2e2; color: #991b1b; }
        .enrich-officer-link { background: none; border: none; padding: 0; cursor: pointer; color: #2563eb; font-size: var(--text-xs); text-decoration: underline; font-family: inherit; }
        .enrich-more__section-title { font-size: var(--text-xs); font-weight: var(--font-weight-semibold); margin: 8px 0 4px; }
        .enrich-more__downloads { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
        .enrich-download-btn { display: inline-block; padding: 5px 10px; font-size: var(--text-xs); background: var(--bg-subtle); border: 1px solid var(--border); border-radius: 5px; color: var(--text); text-decoration: none; cursor: pointer; }
        .enrich-download-btn:hover { background: var(--bg-card); border-color: var(--border-strong); }
        .enrich-skipped { font-size: var(--text-xs); color: var(--text-muted); font-style: italic; }
        .enrich-disq-status { font-size: var(--text-xs); margin-top: 8px; }
        .enrich-label { color: var(--text-muted); margin-right: 4px; }
        .enrich-add-all-btn { margin-bottom: 8px; display: block; }

        /* ── Intelligence panel ── */
        .intel-panel { margin-top: 12px; border-top: 1px solid var(--border); padding-top: 10px; display: flex; flex-direction: column; gap: 8px; }
        .intel-section { display: flex; flex-direction: column; gap: 4px; }
        .intel-section__title { font-size: var(--text-xs); font-weight: var(--font-weight-semibold); text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 4px; }
        .intel-flag { display: flex; align-items: flex-start; gap: 6px; font-size: var(--text-xs); line-height: 1.4; }
        .intel-flag__icon { font-size: var(--text-sm); flex-shrink: 0; margin-top: 1px; }
        .intel-flag__icon--high   { color: #dc2626; }
        .intel-flag__icon--medium { color: #f59e0b; }
        .intel-flag__icon--ok     { color: #16a34a; }
        .intel-flag__text { color: var(--text); }
        .intel-flag--high   .intel-flag__text { color: #dc2626; font-weight: 500; }
        .intel-flag--medium .intel-flag__text { color: #92400e; }
        .intel-flag--ok     .intel-flag__text { color: #14532d; }
        .intel-risk-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: var(--text-xs); font-weight: var(--font-weight-semibold); margin-bottom: 4px; }
        .intel-risk-badge--high   { background: #fee2e2; color: #dc2626; }
        .intel-risk-badge--medium { background: #fef3c7; color: #92400e; }
        .intel-risk-badge--low    { background: #dcfce7; color: #14532d; }
        .intel-signal { font-size: var(--text-xs); color: var(--text); padding-left: 10px; }
        .intel-signal__text::before { content: "• "; color: var(--text-muted); }
        .intel-tenure { font-size: var(--text-xs); color: var(--text-muted); margin-top: 2px; }
        .intel-tenure__summary { line-height: 1.5; }
        .intel-colocation { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 4px; }
        .intel-colocation__label { font-size: var(--text-xs); color: var(--text); }
        .intel-colocation__btn { font-size: var(--text-xs); padding: 3px 8px; background: var(--bg-subtle); border: 1px solid var(--border); border-radius: 4px; cursor: pointer; color: var(--text); white-space: nowrap; }
        .intel-colocation__btn:hover { background: var(--bg-card); border-color: var(--border-strong); }

        /* ── Ownership chain ── */
        .ownership-chain__level-label { font-size: var(--text-xs); font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 6px; padding-bottom: 2px; border-bottom: 1px solid var(--border); }
        .ownership-chain__row { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; padding: 5px 0; border-bottom: 1px solid var(--border); }
        .ownership-chain__row--ceased { opacity: 0.45; }
        .ownership-chain__info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
        .ownership-chain__name-row { display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }
        .ownership-chain__name { font-size: var(--text-sm); font-weight: 500; color: var(--text); word-break: break-word; }
        .ownership-chain__badge { font-size: 10px; padding: 1px 5px; border-radius: 3px; font-weight: 600; white-space: nowrap; }
        .ownership-chain__badge--offshore { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
        .ownership-chain__badge--ceased { background: var(--bg-subtle); color: var(--text-muted); border: 1px solid var(--border); }
        .ownership-chain__detail { display: flex; flex-direction: column; gap: 1px; }
        .ownership-chain__meta { font-size: var(--text-xs); color: var(--text-muted); }
        .ownership-chain__noc { font-size: var(--text-xs); color: var(--text-muted); font-style: italic; }
        .ownership-chain__add-btn { font-size: var(--text-xs); padding: 3px 7px; background: var(--bg-subtle); border: 1px solid var(--border); border-radius: 4px; cursor: pointer; color: var(--text); white-space: nowrap; flex-shrink: 0; align-self: center; }
        .ownership-chain__add-btn:hover { background: var(--bg-card); border-color: var(--border-strong); }

        /* ── Status page ── */
        .status-page-scroll { flex: 1; overflow-y: auto; overflow-x: hidden; cursor: grab; user-select: none; }
        .status-page-scroll.is-dragging { cursor: grabbing; }
        .status-page { padding: 40px 24px 32px; max-width: 860px; margin: 0 auto; }
        .status-page__subtitle { font-size: var(--text-base); color: var(--text-muted); margin-bottom: 32px; text-align: center; }
        .status-body { display: flex; flex-direction: column; gap: 32px; }
        .status-section { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
        .status-section__title { font-size: var(--text-sm); font-weight: var(--font-weight-bold); text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); padding: 10px 16px; background: var(--bg-subtle); border-bottom: 1px solid var(--border); }
        .status-section__note { font-size: var(--text-sm); color: var(--text-muted); padding: 8px 16px 0; margin: 0; }
        .status-table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
        .status-table__head { text-align: left; font-weight: var(--font-weight-semibold); font-size: var(--text-xs); text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); padding: 8px 16px; background: var(--bg-subtle); border-bottom: 1px solid var(--border); }
        .status-table td { padding: 10px 16px; border-bottom: 1px solid var(--border); vertical-align: middle; }
        .status-table tr:last-child td { border-bottom: none; }
        .status-table__label { font-weight: 500; }
        .status-badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: var(--text-xs); font-weight: var(--font-weight-semibold); text-transform: uppercase; letter-spacing: 0.04em; }
        .status-badge--ok   { background: #d1fae5; color: #065f46; }
        .status-badge--down { background: #fee2e2; color: #991b1b; }
        .status-bar { width: 120px; height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
        .status-bar__fill { height: 100%; background: var(--accent); border-radius: 4px; transition: width 0.3s; }
        .status-bar__fill--warn { background: #f59e0b; }
    """)


def get_critical_canvas_style(bg: str = "#09090b", fg: str = "#fafafa"):
    """Runs before @import/fonts in other stylesheets so the first paint is not browser-white (FOUC)."""
    return Style(
        f"html{{color-scheme:dark;background-color:{bg};}}body{{background-color:{bg};color:{fg};}}"
    )


def get_app_style():
    return Style("""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap');

        :root {
            /* Typography */
            --font-display: "Space Grotesk", system-ui, sans-serif;
            --font-body: "Inter", system-ui, sans-serif;
            --font-mono: "JetBrains Mono", ui-monospace, monospace;

            /* Dark Palette (Default) */
            --bg-page: #09090b;
            --bg-elevated: #111114;
            --bg-surface: #18181b;
            --bg-card: #18181b;
            --bg-muted: #27272a;
            --text-main: #fafafa;
            --text-muted: #a1a1aa;
            --text-faint: #52525b;
            
            --accent: #6366f1;
            --accent-hover: #4f46e5;
            --accent-light: rgba(99, 102, 241, 0.15);
            
            --brand-green: #10b981;
            --brand-error: #ef4444;
            
            --border: rgba(255, 255, 255, 0.08);
            --border-subtle: rgba(255, 255, 255, 0.04);
            --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
            --glass-bg: rgba(17, 17, 20, 0.85);

            /* Surfaces (Static) */
            --surface-light: #FFFFFF;
            --text-on-light: #0f172a;
            --border-light: #e2e8f0;
            /* Chromium (Chrome/Edge): system focus ring colour */
            -webkit-focus-ring-color: transparent;
        }

        html[data-theme="light"] {
            --bg-page: #f8fafc;
            --bg-elevated: #ffffff;
            --bg-surface: #f1f5f9;
            --bg-card: #ffffff;
            --bg-muted: #e2e8f0;
            --text-main: #020617;
            --text-muted: #64748b;
            --text-faint: #94a3b8;
            
            --accent: #4f46e5;
            --accent-hover: #4338ca;
            --accent-light: rgba(79, 70, 229, 0.1);
            
            --border: rgba(15, 23, 42, 0.08);
            --border-subtle: rgba(15, 23, 42, 0.04);
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --glass-bg: rgba(255, 255, 255, 0.85);
        }

        *, *::before, *::after { box-sizing: border-box; }

        html {
            border: none !important;
            outline: none !important;
        }

        body.app-layout {
            background-color: var(--bg-page);
            color: var(--text-main);
            font-family: var(--font-body);
            margin: 0; padding: 0;
            border: none !important;
            outline: none !important;
            display: flex; flex-direction: column;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        html:focus,
        html:focus-visible,
        html:focus-within,
        body.app-layout:focus,
        body.app-layout:focus-visible,
        body.app-layout:focus-within,
        .app-layout:focus,
        .app-layout:focus-visible,
        main:focus,
        main:focus-visible,
        body.app-layout > div:first-child:focus,
        body.app-layout > div:first-child:focus-visible {
            outline: none !important;
            box-shadow: none !important;
        }

        a,
        a:hover,
        a:active,
        button {
            -webkit-tap-highlight-color: transparent;
        }

        a:focus,
        a:focus-visible,
        a:active,
        button:focus,
        button:focus-visible {
            outline: none !important;
            box-shadow: none !important;
        }

        a:focus-visible,
        button:focus-visible {
            outline: 2px solid color-mix(in srgb, var(--text-main) 65%, transparent) !important;
            outline-offset: 3px;
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
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        select, select option {
            background: var(--bg-surface);
            color: var(--text-main);
        }
        select option:checked {
            background: var(--accent);
            color: #ffffff;
        }
        input.odl-input:focus, select.odl-input:focus {
            outline: none; border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-light);
        }

        button.odl-btn-primary {
            background: var(--accent); color: #ffffff; border: none;
            padding: 11px 22px; border-radius: 8px; font-weight: 600;
            font-size: 14px; font-family: var(--font-body);
            letter-spacing: -0.01em; cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button.odl-btn-primary:hover { 
            background: var(--accent-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        }
        button.odl-btn-primary:active {
            transform: translateY(0);
        }

        .success-text { color: var(--brand-green); font-size: 14px; }
        .error-text   { color: var(--brand-error); font-size: 14px; }
    """)


def get_shared_style():
    return Style("""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Roboto+Mono:wght@400;700&display=swap');
        :root {
            -webkit-focus-ring-color: transparent;
            --odl-bg: #f7f7f4; --odl-bg-elevated: #ffffff;
            --odl-border-subtle: rgba(0, 0, 0, 0.1);
            --odl-text: #111827; --odl-text-muted: #4b5563;
            --odl-accent: #f97316; --odl-accent-soft: rgba(249, 115, 22, 0.15);
            --odl-font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        * { box-sizing: border-box; }

        html {
            border: none !important;
            outline: none !important;
        }

        body {
            background-color: var(--odl-bg) !important;
            color: var(--odl-text) !important;
            font-family: var(--odl-font-family) !important;
            margin: 0;
            padding: 0;
            border: none !important;
            outline: none !important;
            -webkit-font-smoothing: antialiased;
        }

        html:focus,
        html:focus-visible,
        html:focus-within,
        body:focus,
        body:focus-visible,
        body:focus-within {
            outline: none !important;
            box-shadow: none !important;
        }

        a,
        a:hover,
        a:active,
        button {
            -webkit-tap-highlight-color: transparent;
        }

        a:focus,
        a:focus-visible,
        a:active,
        button:focus,
        button:focus-visible {
            outline: none !important;
            box-shadow: none !important;
        }

        a:focus-visible,
        button:focus-visible {
            outline: 2px solid rgba(17, 24, 39, 0.4) !important;
            outline-offset: 3px;
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


def get_focus_ring_reset_style():
    """Pages with a custom Html/Head that do not load get_app_style() (auth, etc.)."""
    return Style("""
        :root {
            -webkit-focus-ring-color: transparent;
        }
        html {
            border: none !important;
            outline: none !important;
        }
        body {
            border: none !important;
            outline: none !important;
        }
        html:focus,
        html:focus-visible,
        html:focus-within,
        body:focus,
        body:focus-visible,
        body:focus-within {
            outline: none !important;
            box-shadow: none !important;
        }
        a,
        a:hover,
        a:active,
        button {
            -webkit-tap-highlight-color: transparent;
        }
        a:focus,
        a:focus-visible,
        a:active,
        button:focus,
        button:focus-visible {
            outline: none !important;
            box-shadow: none !important;
        }
        a:focus-visible,
        button:focus-visible {
            outline: 2px solid rgba(248, 250, 252, 0.45) !important;
            outline-offset: 3px;
        }
    """)
