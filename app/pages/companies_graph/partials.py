"""
HTMX partial responses: search results, graph element payloads, entity detail panel.
"""
from __future__ import annotations

import json

from fasthtml.common import (
    A, Button, Div, H3, Input, NotStr, P, Script, Span,
    Table, Tbody, Td, Th, Thead, Tr, FT,
)

from .cyto import graph_data_to_cyto


def search_results_partial(search_data: dict) -> FT:
    """
    Returns HTML items for the additive search results list.
    Rendered into #search-results-incoming; JS merges into #search-results-items.
    """
    results = search_data.get("results", [])
    if not results:
        return Div(cls="search-results__empty")

    items = []
    for r in results:
        kind = r.get("kind", "company")
        name = r.get("name", "")
        entity_id = r.get("id", "")
        status = r.get("status", "")
        address = r.get("address_snippet", "")
        date_created = r.get("date_of_creation", "")
        description = r.get("description", "")
        appointments = r.get("appointments_count")
        disq_until = r.get("disqualified_until")

        if kind == "company":
            badge_text = "Company"
            badge_cls = "search-result__badge--company"
            status_cls = f"search-result__status--{status}" if status else ""
            meta_parts = [p for p in [address, f"Est. {date_created}" if date_created else ""] if p]
            meta = " · ".join(meta_parts)
        elif kind == "disqualified-officer":
            badge_text = "Disq"
            badge_cls = "search-result__badge--disqualified"
            status_cls = "search-result__status--disqualified"
            status = f"Disqualified until {disq_until}" if disq_until else "Disqualified"
            meta = description or ""
        else:
            badge_text = "Person"
            badge_cls = "search-result__badge--person"
            status_cls = ""
            status = description or ""
            meta = f"{appointments} appointments" if appointments else ""

        meta_spans = [Span(badge_text, cls=f"search-result__badge {badge_cls}")]
        if status:
            meta_spans.append(Span(status, cls=f"search-result__status {status_cls}"))
        if meta:
            meta_spans.append(Span(meta, cls="search-result__meta"))

        items.append(
            Span(
                Span(Span(cls="search-result__check-box"), cls="search-result__check-wrap"),
                Div(
                    Span(name, cls="search-result__name"),
                    Div(*meta_spans, cls="search-result__row2"),
                    cls="search-result__body",
                ),
                Span(**{
                    "data-cb-value": f"{kind}:{entity_id}",
                    "data-cb-name": name,
                    "class": "search-result__cb-data",
                }),
                cls="search-result__item",
                **{"data-kind": kind, "data-id": entity_id, "data-checked": "false"},
                onclick="toggleSearchResultItem(this)",
            )
        )

    return Div(*items)


def graph_elements_response(graph_data: dict) -> FT:
    """
    Returns a hidden <script type="application/json"> tag containing the
    Cytoscape elements array. JS reads and calls mergeElements(), then removes it.
    """
    elements = graph_data_to_cyto(graph_data)
    return Script(
        NotStr(json.dumps(elements)),
        id="graph-data-payload",
        type="application/json",
    )


def entity_detail_panel(entity_type: str, entity_data: dict, node_id: str) -> FT:
    """Sidebar detail panel rendered when a node is tapped."""
    props = entity_data.get("props", {})
    label = entity_data.get("label", node_id)

    skip = {"number", "id", "updated_at"}
    rows = []
    if entity_type == "Person":
        rows.append(Tr(
            Th("Person Id", cls="graph-sidebar__th"),
            Td(f"p:{node_id}", cls="graph-sidebar__td"),
        ))
    for k, v in props.items():
        if k in skip or not v:
            continue
        display_val = ", ".join(v) if isinstance(v, list) else str(v)
        rows.append(Tr(
            Th(k.replace("_", " ").title(), cls="graph-sidebar__th"),
            Td(display_val, cls="graph-sidebar__td"),
        ))

    badge_mod = entity_type.lower()

    # Cyto node ID used for risk level application
    cyto_node_id = f"{'c' if entity_type == 'Company' else 'p'}_{node_id}"

    expand_controls = Div(
        Button(
            "Show relationships",
            id="sidebar-expand-btn",
            data_node_type=entity_type,
            data_node_id=node_id,
            cls="graph-sidebar__expand-btn",
        ),
        *(
            [Button(
                "\u26a1 Full CH Enrichment",
                id="sidebar-enrich-btn",
                data_entity_type=entity_type,
                data_entity_id=node_id,
                cls="graph-sidebar__enrich-btn",
                onclick=f"startEnrichment('{entity_type}', '{node_id}')",
            )]
            if entity_type in ("Company", "Person") else []
        ),
        cls="graph-sidebar__expand-section",
    )

    # Intelligence panels — loaded via HTMX on node tap
    intelligence_panel = Div(id="intelligence-panel")
    if entity_type == "Company":
        intelligence_panel = Div(
            Div(
                id="company-health-panel",
                hx_get=f"/companies-graph/intelligence/company/{node_id}",
                hx_trigger="load",
                hx_swap="innerHTML",
            ),
            Div(
                id="company-ownership-panel",
                hx_get=f"/companies-graph/intelligence/company/{node_id}/ownership",
                hx_trigger="load",
                hx_swap="innerHTML",
            ),
            id="intelligence-panel",
        )
    elif entity_type == "Person":
        intelligence_panel = Div(
            id="intelligence-panel",
            hx_get=f"/companies-graph/intelligence/person/{node_id}",
            hx_trigger="load",
            hx_swap="innerHTML",
            # Pass the cyto node ID so JS can apply risk_level colour
            **{"data-cyto-node-id": cyto_node_id},
        )

    return Div(
        H3(label, cls="graph-sidebar__name"),
        Span(entity_type, cls=f"graph-sidebar__badge graph-sidebar__badge--{badge_mod}"),
        Table(*rows, cls="graph-sidebar__table") if rows else Div(),
        expand_controls,
        intelligence_panel,
        Div(id="enrichment-panel") if entity_type in ("Company", "Person") else Div(),
        cls="graph-sidebar__detail",
    )
