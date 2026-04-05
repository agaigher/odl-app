"""
Full-page layout for the Companies Graph — canvas, left panel, sidebar, bottom bar.
"""
from __future__ import annotations

from fasthtml.common import (
    A, Button, Div, Form, Input, Label, NotStr, P, Script, Span, FT,
)
from app.ui.components import module_page_layout
from app.ui.styles import get_graph_style
from .js import build_js

CYTOSCAPE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.29.2/cytoscape.min.js"


def _left_panel() -> FT:
    return Div(
        Div(
            Form(
                Input(
                    type="text",
                    id="graph-search-input",
                    name="query",
                    placeholder="Search companies & people...",
                    cls="graph-search__input",
                    autocomplete="off",
                ),
                Button("Search", type="submit", cls="graph-search__btn"),
                Button("Clear search", type="button", id="btn-clear-search",
                       cls="graph-search__btn graph-search__btn--clear"),
                hx_post="/companies-graph/search",
                hx_target="#search-results-incoming",
                hx_swap="innerHTML",
                hx_indicator="#graph-spinner",
                cls="graph-search__form",
            ),
            Div(id="graph-spinner", cls="graph-spinner htmx-indicator"),
            cls="graph-panel__section",
        ),
        Div(
            Div(
                Span("", id="search-results-count", cls="search-results__count"),
                A("Clear selection", href="#", id="btn-clear-selection",
                  cls="search-results__clear", style="display:none;"),
                cls="search-results__header",
                id="search-results-header",
                style="display:none;",
            ),
            Div(id="search-results-items", cls="search-results__items"),
            Div(id="search-results-incoming", style="display:none;"),
            cls="graph-panel__section graph-panel__section--results",
            id="search-results-panel",
        ),
        Div(
            Button("Add to Graph", id="btn-add-to-graph",
                   cls="graph-search__btn graph-search__btn--add", disabled=True),
            Span("0 selected", id="selection-count-label", cls="graph-panel__hint"),
            cls="graph-panel__section",
            id="add-to-graph-section",
            style="display:none;",
        ),
        Div(cls="graph-left-panel__resize-handle", id="left-panel-resize-handle"),
        cls="graph-left-panel",
    )


def _bottom_bar() -> FT:
    return Div(
        Button("\u2212", id="btn-zoom-out", cls="graph-nav__btn", title="Zoom out"),
        Button("+", id="btn-zoom-in", cls="graph-nav__btn", title="Zoom in"),
        Button("Fit", id="btn-fit", cls="graph-nav__btn", title="Fit view"),
        Div(cls="graph-nav__divider"),
        Button("Path", id="btn-path-mode", cls="graph-nav__btn", title="Find path between two nodes"),
        Span("Click two nodes", id="path-hint", style="display:none;", cls="graph-nav__path-hint"),
        Div(cls="graph-nav__divider"),
        Div(
            Span("Depth", cls="graph-nav__depth-label"),
            Input(type="range", id="global-depth-slider", min="1", max="4", value="1", step="1",
                  cls="graph-nav__slider"),
            Span("1", id="global-depth-label", cls="graph-nav__depth-val"),
            cls="graph-nav__depth-group",
        ),
        Div(cls="graph-nav__divider"),
        # Nodes filter dropdown
        Div(
            Button("Nodes \u25be", cls="graph-nav__btn graph-nav__dropdown-trigger",
                   id="nodes-dropdown-trigger"),
            Div(
                Label(Input(type="checkbox", cls="graph-filter-node-all", checked=True), " All",
                      cls="graph-nav__dropdown-item"),
                Label(Input(type="checkbox", cls="graph-filter-node", data_type="Company", checked=True), " Company",
                      cls="graph-nav__dropdown-item"),
                Label(Input(type="checkbox", cls="graph-filter-node", data_type="Person", checked=True), " Person",
                      cls="graph-nav__dropdown-item"),
                Label(Input(type="checkbox", cls="graph-filter-node", data_type="InsolvencyCase", checked=True), " InsolvencyCase",
                      cls="graph-nav__dropdown-item"),
                Label(Input(type="checkbox", cls="graph-filter-node", data_type="Charge", checked=True), " Charge",
                      cls="graph-nav__dropdown-item"),
                cls="graph-nav__dropdown-menu",
                id="nodes-dropdown-menu",
            ),
            cls="graph-nav__dropdown",
        ),
        # Relationships filter dropdown
        Div(
            Button("Relationships \u25be", cls="graph-nav__btn graph-nav__dropdown-trigger",
                   id="rels-dropdown-trigger"),
            Div(
                Label(Input(type="checkbox", cls="graph-filter-rel-all", checked=True), " All",
                      cls="graph-nav__dropdown-item"),
                *[Label(Input(type="checkbox", cls="graph-filter-rel", data_type=rt, checked=True),
                        f" {rt}", cls="graph-nav__dropdown-item")
                  for rt in ["OFFICER", "PSC", "OFFICER_CORPORATE", "PSC_CORPORATE",
                              "BRANCH_OF", "HAS_INSOLVENCY_CASE", "PRACTITIONER_IN",
                              "HAS_CHARGE", "DISQUALIFIED_FROM"]],
                cls="graph-nav__dropdown-menu",
                id="rels-dropdown-menu",
            ),
            cls="graph-nav__dropdown",
        ),
        Div(cls="graph-nav__divider"),
        Div(
            Label("BG", cls="graph-nav__color-label"),
            Input(type="color", id="color-bg", value="#fafafa", cls="graph-nav__color", title="Background color"),
            cls="graph-nav__color-group",
        ),
        Div(
            Label("Co", cls="graph-nav__color-label"),
            Input(type="color", id="color-company", value="#0057ff", cls="graph-nav__color", title="Company node color"),
            cls="graph-nav__color-group",
        ),
        Div(
            Label("Pe", cls="graph-nav__color-label"),
            Input(type="color", id="color-person", value="#ff6961", cls="graph-nav__color", title="Person node color"),
            cls="graph-nav__color-group",
        ),
        Div(cls="graph-nav__divider"),
        Button("Clear", id="btn-graph-clear", cls="graph-nav__btn graph-nav__btn--danger", title="Clear graph"),
        cls="graph-bottom-bar",
    )


def _sidebar() -> FT:
    return Div(
        Div(cls="graph-sidebar__resize-handle", id="sidebar-resize-handle"),
        Div(
            P("Click a node to see details", cls="graph-sidebar__placeholder"),
            id="graph-sidebar-content",
        ),
        cls="graph-sidebar",
        id="graph-sidebar",
    )


def companies_graph_page(user_email: str = "", session=None) -> FT:
    main_content = Div(
        get_graph_style(),
        Div(id="cy", cls="graph-canvas"),
        _left_panel(),
        _sidebar(),
        _bottom_bar(),
        Div(id="graph-htmx-target", style="display:none;"),
        Script(src=CYTOSCAPE_CDN),
        Script(NotStr(build_js())),
        cls="graph-page",
    )
    return module_page_layout(
        "Companies Graph", "/companies-graph", user_email,
        main_content,
        session=session, active_module="explore", show_sidebar=False,
    )
