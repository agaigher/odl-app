"""
Companies Graph routes — canvas page, HTMX partials, intelligence, status.
"""
from __future__ import annotations

import asyncio
import json

from fasthtml.common import NotStr, Script
from starlette.responses import JSONResponse, Response

from app.pages.companies_graph import (
    companies_graph_page,
    graph_elements_response,
    search_results_partial,
    entity_detail_panel,
    enrichment_spinner,
    enrichment_panel,
    enrichment_error,
    officer_enrichment_panel,
    company_health_panel,
    ownership_chain_panel,
    person_intelligence_panel,
    person_intelligence_error,
    graph_data_to_cyto,
)
from app.pages.graph_status import (
    graph_status_page,
    graph_status_panel,
    _fetch_status,
)
from app.graph_client import (
    graph_expand,
    graph_entity,
    graph_path,
    graph_ch_search,
    graph_resolve_person,
    graph_start_enrich,
    graph_enrich_status,
    graph_download_cached,
    graph_company_health,
    graph_ownership_chain,
    graph_person_risk,
    graph_person_tenure,
    graph_co_located,
    GraphAPIError,
)


def register(rt):

    @rt("/companies-graph")
    def get_companies_graph(session):
        user_email = session.get("user", "")
        return companies_graph_page(user_email=user_email, session=session)

    @rt("/companies-graph/search", methods=["POST"])
    async def post_companies_graph_search(session, query: str = ""):
        if not query.strip():
            from fasthtml.common import Div
            return Div()
        try:
            data = await graph_ch_search(query=query.strip(), limit=20)
            return search_results_partial(data)
        except GraphAPIError as e:
            from fasthtml.common import Div
            return Div(f"Search unavailable: {e}", cls="error-text")

    @rt("/companies-graph/add-nodes", methods=["POST"])
    async def post_companies_graph_add_nodes(session, request):
        from fasthtml.common import Div
        form = await request.form()
        node_values = form.getlist("node")
        if not node_values:
            return Div()

        _kind_to_node_type = {
            "company":              "Company",
            "officer":              "Person",
            "disqualified-officer": "Person",
        }

        nodes = []
        for val in node_values:
            parts = val.split(":", 1)
            if len(parts) == 2:
                kind, entity_id = parts
                node_type = _kind_to_node_type.get(kind)
                if node_type:
                    nodes.append({"node_type": node_type, "id": entity_id, "ch_id": entity_id})
        if not nodes:
            return Div()

        for node in nodes:
            if node["node_type"] == "Person":
                try:
                    resolved = await graph_resolve_person(node["ch_id"])
                    if resolved:
                        node["id"] = resolved
                except GraphAPIError:
                    pass

        all_elements: list[dict] = []
        seen_node_ids: set[str] = set()
        for node in nodes:
            try:
                data = await graph_expand(
                    node_id=node["id"],
                    node_type=node["node_type"],
                    depth=1,
                    active_only=False,
                )
                for el in graph_data_to_cyto(data):
                    if el["data"]["id"] not in seen_node_ids:
                        seen_node_ids.add(el["data"]["id"])
                        all_elements.append(el)
            except GraphAPIError:
                pass

        return Script(
            NotStr(json.dumps(all_elements)),
            id="graph-data-payload",
            type="application/json",
        )

    @rt("/companies-graph/expand/{node_id}", methods=["POST"])
    async def post_companies_graph_expand(
        session, node_id: str, node_type: str = "Company", depth: int = 1
    ):
        from fasthtml.common import Div
        depth = max(1, min(depth, 4))
        try:
            data = await graph_expand(node_id=node_id, node_type=node_type, depth=depth)
            return graph_elements_response(data)
        except GraphAPIError as e:
            return Div(f"Graph unavailable: {e}", cls="error-text")

    @rt("/companies-graph/entity/{entity_type}/{entity_id:path}")
    async def get_companies_graph_entity(session, entity_type: str, entity_id: str):
        from fasthtml.common import Div
        try:
            data = await graph_entity(entity_type=entity_type, entity_id=entity_id)
            return entity_detail_panel(entity_type, data, entity_id)
        except GraphAPIError as e:
            return Div(f"Could not load entity: {e}", cls="graph-sidebar__placeholder")

    @rt("/companies-graph/enrich/{entity_type}/{entity_id:path}", methods=["POST"])
    async def post_enrich_entity(session, entity_type: str, entity_id: str):
        try:
            result = await graph_start_enrich(entity_type, entity_id)
            job_id = result.get("job_id", "")
            return enrichment_spinner(job_id)
        except GraphAPIError as e:
            return enrichment_error(str(e))

    @rt("/companies-graph/enrich/status/{job_id}")
    async def get_enrich_status_poll(session, job_id: str):
        try:
            data = await graph_enrich_status(job_id)
        except GraphAPIError as e:
            return enrichment_error(str(e))

        status = data.get("status", "running")
        if status == "running":
            return enrichment_spinner(job_id)
        if status == "error":
            return enrichment_error(data.get("error") or "Unknown error")
        entity_type = data.get("entity_type", "Company")
        entity_id = data.get("entity_id", "")
        if entity_type == "Person":
            return officer_enrichment_panel(data, entity_id)
        return enrichment_panel(data, entity_id)

    @rt("/companies-graph/download/{entity_id}/{endpoint_key}")
    async def get_download_cached(session, entity_id: str, endpoint_key: str):
        try:
            content = await graph_download_cached(entity_id, endpoint_key)
            filename = f"{entity_id}_{endpoint_key}.json"
            return Response(
                content=content,
                media_type="application/json",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        except GraphAPIError as e:
            return Response(f"Download failed: {e}", status_code=502)

    @rt("/companies-graph/path")
    async def get_companies_graph_path(
        session,
        from_id: str = "",
        from_type: str = "Company",
        to_id: str = "",
        to_type: str = "Company",
        max_hops: int = 4,
    ):
        max_hops = max(1, min(max_hops, 6))
        try:
            data = await graph_path(from_id, from_type, to_id, to_type, max_hops)
            elements = graph_data_to_cyto(data)
            path_ids = [e["data"]["id"] for e in elements]
            return JSONResponse({"elements": elements, "path_ids": path_ids})
        except GraphAPIError as e:
            return JSONResponse({"elements": [], "path_ids": [], "error": str(e)})

    @rt("/companies-graph/intelligence/company/{company_number}")
    async def get_company_intelligence(session, company_number: str):
        from fasthtml.common import Div
        try:
            health, co_location = await asyncio.gather(
                graph_company_health(company_number),
                graph_co_located(company_number),
                return_exceptions=True,
            )
            if isinstance(health, Exception):
                health = {}
            if isinstance(co_location, Exception):
                co_location = []
            return company_health_panel(health, co_location, company_number)
        except Exception:
            return Div(cls="intel-panel")

    @rt("/companies-graph/intelligence/company/{company_number}/ownership")
    async def get_company_ownership(session, company_number: str):
        from fasthtml.common import Div
        try:
            chain = await graph_ownership_chain(company_number)
            return ownership_chain_panel(chain)
        except Exception:
            return Div(cls="intel-section")

    @rt("/companies-graph/intelligence/person/{officer_id}")
    async def get_person_intelligence(session, request, officer_id: str):
        cyto_node_id = request.headers.get("HX-Trigger-Name", "") or f"p_{officer_id}"
        try:
            risk, tenure = await asyncio.gather(
                graph_person_risk(officer_id),
                graph_person_tenure(officer_id),
                return_exceptions=True,
            )
            if isinstance(risk, Exception):
                risk = {}
            if isinstance(tenure, Exception):
                tenure = {}
            return person_intelligence_panel(risk, tenure, cyto_node_id)
        except Exception:
            return person_intelligence_error()

    @rt("/companies-graph/status")
    async def get_graph_status(session):
        user_email = session.get("user", "")
        status = await _fetch_status()
        return graph_status_page(user_email=user_email, status=status, session=session)

    @rt("/companies-graph/status/poll")
    async def get_graph_status_poll(session):
        status = await _fetch_status()
        return graph_status_panel(status)
