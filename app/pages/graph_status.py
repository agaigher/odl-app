"""
Companies Graph status page.

Shows live health of all Mac Mini infrastructure components:
  - Cloudflare Tunnel / FastAPI reachability
  - Neo4j and PostgreSQL connectivity
  - Node/row counts across both databases
  - Stream worker offset status for all 9 CH streams

The page auto-refreshes every 30 seconds via HTMX polling.
"""
from __future__ import annotations

import httpx
import os

from fasthtml.common import (
    A, Button, Div, H2, NotStr, P, Script, Span, Table, Td, Th, Tr, FT,
)
from app.ui.components import module_page_layout
from app.ui.styles import get_graph_style

ODL_GRAPH_API_URL = os.environ.get("ODL_GRAPH_API_URL", "").rstrip("/")
ODL_GRAPH_API_KEY = os.environ.get("ODL_GRAPH_API_KEY", "")
_TIMEOUT = 8.0

ALL_STREAMS = [
    "/companies",
    "/officers",
    "/persons-with-significant-control",
    "/filings",
    "/insolvency-cases",
    "/charges",
    "/disqualified-officers",
    "/company-exemptions",
    "/persons-with-significant-control-statements",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _badge(ok: bool, ok_text: str = "OK", fail_text: str = "DOWN") -> FT:
    cls = "status-badge status-badge--ok" if ok else "status-badge status-badge--down"
    return Span(ok_text if ok else fail_text, cls=cls)


def _row(label: str, *cells) -> FT:
    return Tr(Td(label, cls="status-table__label"), *[Td(c) for c in cells])


# ---------------------------------------------------------------------------
# Data fetching  (called from the route — runs server-side on Vercel)
# ---------------------------------------------------------------------------

async def _fetch_status() -> dict:
    """Call the Mac Mini graph API for health + stats. Returns a status dict."""
    result = {
        "api_ok": False,
        "neo4j_ok": False,
        "postgres_ok": False,
        # Neo4j counts
        "neo4j_companies": None,
        "neo4j_persons": None,
        "psc_rel_count": None,
        "officer_rel_count": None,
        "corp_rel_count": None,
        # Postgres counts
        "pg_companies": None,
        "pg_officers": None,
        "pg_pscs": None,
        "pg_filings": None,
        "pg_charges": None,
        "pg_insolvency_cases": None,
        "pg_disqualified_officers": None,
        "pg_psc_statements": None,
        "pg_company_exemptions": None,
        # Stream offsets — list of {stream, last_event_id, events_processed, last_received}
        "stream_offsets": [],
        # Mac Mini system metrics
        "system": None,
        "error": None,
    }

    if not ODL_GRAPH_API_URL:
        result["error"] = "ODL_GRAPH_API_URL not configured"
        return result

    headers = {
        "X-API-Key": ODL_GRAPH_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            h = await client.get(f"{ODL_GRAPH_API_URL}/health")
            if h.status_code == 200:
                body = h.json()
                result["api_ok"] = True
                result["neo4j_ok"]    = body.get("neo4j")    == "reachable"
                result["postgres_ok"] = body.get("postgres") == "reachable"

            if result["api_ok"]:
                s = await client.get(f"{ODL_GRAPH_API_URL}/stats", headers=headers)
                if s.status_code == 200:
                    stats = s.json()
                    neo4j = stats.get("neo4j", {})
                    pg    = stats.get("postgres", {})
                    result["neo4j_companies"]   = neo4j.get("companies")
                    result["neo4j_persons"]     = neo4j.get("persons")
                    result["psc_rel_count"]     = neo4j.get("psc_rels")
                    result["officer_rel_count"] = neo4j.get("officer_rels")
                    result["corp_rel_count"]    = neo4j.get("corp_rels")
                    result["pg_companies"]            = pg.get("companies")
                    result["pg_officers"]             = pg.get("officers")
                    result["pg_pscs"]                 = pg.get("pscs")
                    result["pg_filings"]              = pg.get("filings")
                    result["pg_charges"]              = pg.get("charges")
                    result["pg_insolvency_cases"]     = pg.get("insolvency_cases")
                    result["pg_disqualified_officers"]= pg.get("disqualified_officers")
                    result["pg_psc_statements"]       = pg.get("psc_statements")
                    result["pg_company_exemptions"]   = pg.get("company_exemptions")
                    result["stream_offsets"]          = stats.get("stream_offsets", [])
                    result["system"]                  = stats.get("system")

    except Exception as exc:
        result["error"] = str(exc)

    return result


def _fmt(n) -> str:
    if n is None:
        return "—"
    return f"{n:,}"


# ---------------------------------------------------------------------------
# Page components
# ---------------------------------------------------------------------------

def _section(title: str, *content) -> FT:
    return Div(
        H2(title, cls="status-section__title"),
        *content,
        cls="status-section",
    )


def graph_status_panel(status: dict) -> FT:
    """The inner panel — returned for both full page and HTMX poll refresh."""
    api_ok      = status["api_ok"]
    neo4j_ok    = status["neo4j_ok"]
    postgres_ok = status["postgres_ok"]
    error       = status["error"]

    # Build offset lookup: stream → {last_event_id, events_processed, last_received}
    offsets_list = status.get("stream_offsets", [])
    offsets = {o["stream"]: o for o in offsets_list} if isinstance(offsets_list, list) else {}

    # ── Infrastructure ───────────────────────────────────────────────────────
    infrastructure = _section(
        "Infrastructure",
        Table(
            Tr(
                Th("Component",  cls="status-table__head"),
                Th("Status",     cls="status-table__head"),
                Th("Notes",      cls="status-table__head"),
            ),
            _row("Cloudflare Tunnel → graph.opendata.london",
                 _badge(api_ok),
                 "FastAPI reachable" if api_ok else (error or "Cannot reach Mac Mini")),
            _row("Neo4j (graph database)",
                 _badge(neo4j_ok),
                 "bolt://localhost:7687" if neo4j_ok else "Unreachable"),
            _row("PostgreSQL (source of truth)",
                 _badge(postgres_ok),
                 "localhost:5432" if postgres_ok else "Unreachable"),
            cls="status-table",
        ),
    )

    # ── Neo4j graph counts ───────────────────────────────────────────────────
    neo4j_counts = _section(
        "Neo4j — graph data",
        Table(
            Tr(
                Th("Node / Relationship", cls="status-table__head"),
                Th("Count",              cls="status-table__head"),
            ),
            _row("Companies",               _fmt(status["neo4j_companies"])),
            _row("Persons",                 _fmt(status["neo4j_persons"])),
            _row("PSC relationships",       _fmt(status["psc_rel_count"])),
            _row("Officer relationships",   _fmt(status["officer_rel_count"])),
            _row("Corporate PSC links",     _fmt(status["corp_rel_count"])),
            cls="status-table",
        ),
    )

    # ── Postgres row counts ──────────────────────────────────────────────────
    pg_counts = _section(
        "PostgreSQL — row counts",
        Table(
            Tr(
                Th("Table",  cls="status-table__head"),
                Th("Rows",   cls="status-table__head"),
            ),
            _row("ch.companies",            _fmt(status["pg_companies"])),
            _row("ch.officers",             _fmt(status["pg_officers"])),
            _row("ch.pscs",                 _fmt(status["pg_pscs"])),
            _row("ch.filings",              _fmt(status["pg_filings"])),
            _row("ch.charges",              _fmt(status["pg_charges"])),
            _row("ch.insolvency_cases",     _fmt(status["pg_insolvency_cases"])),
            _row("ch.disqualified_officers",_fmt(status["pg_disqualified_officers"])),
            _row("ch.psc_statements",       _fmt(status["pg_psc_statements"])),
            _row("ch.company_exemptions",   _fmt(status["pg_company_exemptions"])),
            cls="status-table",
        ),
    )

    # ── Mac Mini system metrics ───────────────────────────────────────────────
    sys_info = status.get("system") or {}
    def _bar(pct) -> FT:
        cls = "status-bar__fill"
        if pct is not None and pct > 85:
            cls += " status-bar__fill--warn"
        return Div(
            Div(style=f"width:{pct or 0}%", cls=cls),
            cls="status-bar",
        )
    system_section = _section(
        "Mac Mini — system resources",
        Table(
            Tr(
                Th("Resource",  cls="status-table__head"),
                Th("Value",     cls="status-table__head"),
                Th("",          cls="status-table__head"),
            ),
            _row("CPU usage",
                 f"{sys_info.get('cpu_percent', '—')} %" if sys_info else "—",
                 _bar(sys_info.get("cpu_percent")) if sys_info else ""),
            _row("Memory",
                 f"{sys_info.get('mem_used_gb', '—')} / {sys_info.get('mem_total_gb', '—')} GB  ({sys_info.get('mem_percent', '—')} %)" if sys_info else "—",
                 _bar(sys_info.get("mem_percent")) if sys_info else ""),
            _row("Disk",
                 f"{sys_info.get('disk_used_gb', '—')} / {sys_info.get('disk_total_gb', '—')} GB  ({sys_info.get('disk_percent', '—')} %)" if sys_info else "—",
                 _bar(sys_info.get("disk_percent")) if sys_info else ""),
            cls="status-table",
        ),
    )

    # ── Stream worker ────────────────────────────────────────────────────────
    stream_rows = [
        Tr(
            Th("Stream",           cls="status-table__head"),
            Th("Events processed", cls="status-table__head"),
            Th("Last event ID",    cls="status-table__head"),
            Th("Last received",    cls="status-table__head"),
            Th("Status",           cls="status-table__head"),
        )
    ]
    for stream in ALL_STREAMS:
        o = offsets.get(stream, {})
        last_id       = o.get("last_event_id")
        processed     = o.get("events_processed")
        last_received = o.get("last_received", "")
        if last_received and "T" in last_received:
            last_received = last_received.replace("T", " ")[:19]
        elif last_received and "." in last_received:
            last_received = last_received[:19]
        stream_rows.append(
            Tr(
                Td(stream,                        cls="status-table__label"),
                Td(_fmt(processed)),
                Td(last_id or "—"),
                Td(last_received or "—"),
                Td(_badge(bool(last_id), "Receiving", "No events yet")),
            )
        )

    streams = _section(
        "CH Streaming worker — all 9 streams",
        P(
            "Offsets are stored in PostgreSQL (ch.stream_offsets) and updated "
            "atomically with each event. 'No events yet' is normal on weekends "
            "or when CH has no activity.",
            cls="status-section__note",
        ),
        Table(*stream_rows, cls="status-table"),
    )

    return Div(
        infrastructure, system_section, neo4j_counts, pg_counts, streams,
        cls="status-body",
        id="status-body",
        hx_get="/companies-graph/status/poll",
        hx_trigger="every 30s",
        hx_swap="outerHTML",
    )


_DRAG_JS = """
(function () {
  var el = document.getElementById('status-scroll');
  if (!el) return;
  var startY, startX, scrollTop, scrollLeft, down = false;
  el.addEventListener('mousedown', function (e) {
    if (e.button !== 0) return;
    down = true;
    startY = e.clientY;
    startX = e.clientX;
    scrollTop  = el.scrollTop;
    scrollLeft = el.scrollLeft;
    el.classList.add('is-dragging');
    e.preventDefault();
  });
  document.addEventListener('mouseup',  function () { down = false; el.classList.remove('is-dragging'); });
  document.addEventListener('mousemove', function (e) {
    if (!down) return;
    el.scrollTop  = scrollTop  - (e.clientY - startY);
    el.scrollLeft = scrollLeft - (e.clientX - startX);
  });
  el.addEventListener('touchstart', function (e) {
    startY = e.touches[0].clientY;
    startX = e.touches[0].clientX;
    scrollTop  = el.scrollTop;
    scrollLeft = el.scrollLeft;
  }, { passive: true });
  el.addEventListener('touchmove', function (e) {
    el.scrollTop  = scrollTop  - (e.touches[0].clientY - startY);
    el.scrollLeft = scrollLeft - (e.touches[0].clientX - startX);
  }, { passive: true });
})();
"""


def graph_status_page(user_email: str = "", status: dict | None = None, session=None) -> FT:
    if status is None:
        status = {
            "api_ok": False, "neo4j_ok": False, "postgres_ok": False,
            "neo4j_companies": None, "neo4j_persons": None,
            "psc_rel_count": None, "officer_rel_count": None, "corp_rel_count": None,
            "pg_companies": None, "pg_officers": None, "pg_pscs": None,
            "pg_filings": None, "pg_charges": None, "pg_insolvency_cases": None,
            "pg_disqualified_officers": None, "pg_psc_statements": None,
            "pg_company_exemptions": None,
            "stream_offsets": [], "system": None, "error": "Loading…",
        }

    main = Div(
        get_graph_style(),
        Div(
            P(
                "Live health of the Mac Mini graph infrastructure. "
                "Refreshes automatically every 30 seconds.",
                cls="status-page__subtitle",
            ),
            graph_status_panel(status),
            cls="status-page",
        ),
        Script(NotStr(_DRAG_JS)),
        cls="status-page-scroll",
        id="status-scroll",
    )
    return module_page_layout(
        "Graph Status", "/companies-graph/status", user_email,
        main,
        session=session, active_module="explore", show_sidebar=False,
    )
