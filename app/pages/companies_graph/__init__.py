"""
Companies Graph module.

Re-exports everything that main.py and the route handlers import, so the
module swap is transparent to the rest of the app.
"""
from .page import companies_graph_page
from .partials import (
    graph_elements_response,
    search_results_partial,
    entity_detail_panel,
)
from .enrichment import (
    enrichment_spinner,
    enrichment_panel,
    enrichment_error,
    officer_enrichment_panel,
)
from .intelligence import (
    company_health_panel,
    ownership_chain_panel,
    person_intelligence_panel,
    person_intelligence_error,
)
from .cyto import graph_data_to_cyto

# Legacy alias used in main.py
_graph_data_to_cyto = graph_data_to_cyto

__all__ = [
    "companies_graph_page",
    "graph_elements_response",
    "search_results_partial",
    "entity_detail_panel",
    "enrichment_spinner",
    "enrichment_panel",
    "enrichment_error",
    "officer_enrichment_panel",
    "company_health_panel",
    "ownership_chain_panel",
    "person_intelligence_panel",
    "person_intelligence_error",
    "graph_data_to_cyto",
    "_graph_data_to_cyto",
]
