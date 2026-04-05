"""
Cytoscape.js style definition and GraphResponse → Cytoscape elements converter.

NOTE: Cytoscape.js renders to canvas and does NOT support CSS var().
We emit the style as a JSON template with __VAR_xxx__ placeholders.
At runtime, JS resolves them via getComputedStyle() before passing
the style to Cytoscape.  See js.py  resolveCytoStyle().
"""
from __future__ import annotations

import json


# Map of placeholder → CSS custom property name
_CSS_VARS = {
    "__VAR_NODE_COMPANY__":                 "--node-company",
    "__VAR_NODE_COMPANY_DISSOLVED__":       "--node-company-dissolved",
    "__VAR_NODE_COMPANY_BORDER_DISSOLVED__":"--node-company-border-dissolved",
    "__VAR_NODE_PERSON__":                  "--node-person",
    "__VAR_NODE_PERSON_RISK_HIGH__":        "--node-person-risk-high",
    "__VAR_NODE_PERSON_RISK_MEDIUM__":      "--node-person-risk-medium",
    "__VAR_NODE_PERSON_RISK_LOW__":         "--node-person-risk-low",
    "__VAR_NODE_HUB_BORDER__":             "--node-hub-border",
    "__VAR_EDGE_LINE__":                    "--edge-line",
    "__VAR_EDGE_ARROW__":                   "--edge-arrow",
    "__VAR_EDGE_LABEL_BG__":               "--edge-label-bg",
    "__VAR_EDGE_LABEL_COLOR__":            "--edge-label-color",
    "__VAR_EDGE_HIGHLIGHTED__":            "--edge-highlighted",
    "__VAR_NODE_SELECTED_BORDER__":        "--node-selected-border",
    "__VAR_ACCENT__":                      "--accent",
    "__VAR_TEXT__":                         "--text",
}


_CYTO_STYLE = [
    {
        "selector": "node[type='Company']",
        "style": {
            "shape": "ellipse",
            "background-color": "__VAR_NODE_COMPANY__",
            "label": "data(label)",
            "font-size": "11px",
            "font-family": "Inter, sans-serif",
            "text-valign": "bottom",
            "text-halign": "center",
            "text-margin-y": "6px",
            "text-wrap": "wrap",
            "text-max-width": "80px",
            "text-background-color": "__VAR_EDGE_LABEL_BG__",
            "text-background-opacity": 0.75,
            "text-background-padding": "2px",
            "text-background-shape": "roundrectangle",
            "color": "__VAR_TEXT__",
            "width": "80px",
            "height": "80px",
        },
    },
    {
        "selector": "node[type='Company'][status='dissolved']",
        "style": {
            "background-color": "__VAR_NODE_COMPANY_DISSOLVED__",
            "border-style": "dashed",
            "border-width": "2px",
            "border-color": "__VAR_NODE_COMPANY_BORDER_DISSOLVED__",
        },
    },
    {
        "selector": "node[type='Person']",
        "style": {
            "shape": "ellipse",
            "background-color": "__VAR_NODE_PERSON__",
            "label": "data(label)",
            "font-size": "11px",
            "font-family": "Inter, sans-serif",
            "text-valign": "bottom",
            "text-halign": "center",
            "text-margin-y": "6px",
            "text-wrap": "wrap",
            "text-max-width": "64px",
            "text-background-color": "__VAR_EDGE_LABEL_BG__",
            "text-background-opacity": 0.75,
            "text-background-padding": "2px",
            "text-background-shape": "roundrectangle",
            "color": "__VAR_TEXT__",
            "width": "60px",
            "height": "60px",
        },
    },
    # Sprint 5a — Person risk level colours (applied lazily on first node tap)
    {
        "selector": "node[type='Person'][risk_level='high']",
        "style": {"background-color": "__VAR_NODE_PERSON_RISK_HIGH__"},
    },
    {
        "selector": "node[type='Person'][risk_level='medium']",
        "style": {"background-color": "__VAR_NODE_PERSON_RISK_MEDIUM__"},
    },
    {
        "selector": "node[type='Person'][risk_level='low']",
        "style": {"background-color": "__VAR_NODE_PERSON_RISK_LOW__"},
    },
    # Sprint 5f — Hub person: purple border + larger size
    {
        "selector": "node[type='Person'][hub='true']",
        "style": {
            "border-width": "4px",
            "border-color": "__VAR_NODE_HUB_BORDER__",
            "width": "80px",
            "height": "80px",
        },
    },
    {
        "selector": "node:selected",
        "style": {
            "border-width": "3px",
            "border-color": "__VAR_NODE_SELECTED_BORDER__",
            "border-opacity": 0.8,
        },
    },
    {
        "selector": "node.highlighted",
        "style": {
            "border-width": "3px",
            "border-color": "__VAR_NODE_PERSON_RISK_MEDIUM__",
        },
    },
    {
        "selector": "node.faded",
        "style": {"opacity": 0.18},
    },
    {
        "selector": "edge.faded",
        "style": {"opacity": 0.06},
    },
    # Hover state
    {
        "selector": "node:active",
        "style": {
            "overlay-opacity": 0,
        },
    },
    {
        "selector": "node.hovered",
        "style": {
            "border-width": "3px",
            "border-color": "__VAR_ACCENT__",
            "border-opacity": 0.7,
            "shadow-blur": "12px",
            "shadow-color": "__VAR_ACCENT__",
            "shadow-opacity": 0.25,
            "shadow-offset-x": "0px",
            "shadow-offset-y": "0px",
        },
    },
    {
        "selector": "edge",
        "style": {
            "width": 1.5,
            "line-color": "__VAR_EDGE_LINE__",
            "target-arrow-color": "__VAR_EDGE_ARROW__",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "label": "data(label)",
            "font-size": "9px",
            "font-family": "IBM Plex Mono, monospace",
            "color": "__VAR_EDGE_LABEL_COLOR__",
            "text-rotation": "autorotate",
            "text-background-color": "__VAR_EDGE_LABEL_BG__",
            "text-background-opacity": 0.7,
            "text-background-padding": "2px",
        },
    },
    {
        "selector": "edge[is_active='false']",
        "style": {
            "line-style": "dashed",
            "opacity": 0.4,
        },
    },
    {
        "selector": "edge.highlighted",
        "style": {
            "line-color": "__VAR_EDGE_HIGHLIGHTED__",
            "target-arrow-color": "__VAR_EDGE_HIGHLIGHTED__",
            "width": 3,
        },
    },
    # Enriched nodes — amber border after full CH enrichment
    {
        "selector": "node[enriched='true']",
        "style": {
            "border-width": "3px",
            "border-color": "__VAR_NODE_PERSON_RISK_MEDIUM__",
            "border-opacity": 0.9,
        },
    },
]

CYTO_STYLE_JSON = json.dumps(_CYTO_STYLE)

# Export the var map as JS object literal for runtime resolution
CYTO_VAR_MAP_JS = json.dumps({k: v for k, v in _CSS_VARS.items()})


def graph_data_to_cyto(graph_data: dict) -> list[dict]:
    """
    Convert a GraphResponse dict (from graph_client) into a Cytoscape.js
    elements array.

    Node IDs are prefixed (c_ / p_) to namespace Company and Person IDs,
    since CH company numbers and person IDs can theoretically collide.
    """
    elements = []
    _RESERVED = {"id", "raw_id", "label", "type", "source", "target"}

    for node in graph_data.get("nodes", []):
        prefix = "c" if node["type"] == "Company" else "p"
        elements.append({
            "data": {
                "id": f"{prefix}_{node['id']}",
                "raw_id": node["id"],
                "label": node["label"],
                "type": node["type"],
                **{k: (", ".join(v) if isinstance(v, list) else v)
                   for k, v in node.get("props", {}).items()
                   if k not in _RESERVED},
            }
        })

    for edge in graph_data.get("edges", []):
        src_prefix = "c" if edge.get("source_type") == "Company" else "p"
        tgt_prefix = "c" if edge.get("target_type") == "Company" else "p"
        props = edge.get("props", {})
        elements.append({
            "data": {
                "id": edge["id"],
                "source": f"{src_prefix}_{edge['source']}",
                "target": f"{tgt_prefix}_{edge['target']}",
                "label": edge["label"],
                "is_active": str(props.get("is_active", True)).lower(),
                **{k: (", ".join(v) if isinstance(v, list) else str(v))
                   for k, v in props.items()},
            }
        })

    return elements
