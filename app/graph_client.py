"""
Async httpx client wrapping the Mac Mini FastAPI graph service.

All calls use a 9-second timeout to stay inside Vercel's 10s function limit.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

GRAPH_API_URL     = os.environ.get("GRAPH_API_URL", "").rstrip("/")
ODL_GRAPH_API_KEY = os.environ.get("ODL_GRAPH_API_KEY", "")

_TIMEOUT = 9.0


class GraphAPIError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    return {
        "X-API-Key": ODL_GRAPH_API_KEY,
        "Content-Type": "application/json",
    }


async def graph_search(query: str, match: str = "prefix", limit: int = 20) -> dict[str, Any]:
    """POST /search — fulltext search across companies and people, returns GraphResponse dict."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"{GRAPH_API_URL}/search",
                json={"query": query, "kind": "all", "match": match, "limit": limit},
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_expand(
    node_id: str,
    node_type: str,
    depth: int = 1,
    active_only: bool = False,
) -> dict[str, Any]:
    """POST /expand — return connected nodes and edges."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"{GRAPH_API_URL}/expand",
                json={
                    "node_id": node_id,
                    "node_type": node_type,
                    "depth": depth,
                    "active_only": active_only,
                },
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_entity(entity_type: str, entity_id: str) -> dict[str, Any]:
    """GET /entity/{type}/{id} — return entity properties."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/entity/{entity_type}/{entity_id}",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_path(
    from_id: str,
    from_type: str,
    to_id: str,
    to_type: str,
    max_hops: int = 4,
) -> dict[str, Any]:
    """GET /path — shortest path between two entities."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/path",
                params={
                    "from_id": from_id,
                    "from_type": from_type,
                    "to_id": to_id,
                    "to_type": to_type,
                    "max_hops": max_hops,
                },
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_ch_search(query: str, limit: int = 20) -> dict[str, Any]:
    """GET /search/ch — search CH REST API directly (companies + officers + disqualified)."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/search/ch",
                params={"query": query, "limit": limit},
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_health() -> bool:
    """GET /health — returns True if the Mac Mini service is reachable."""
    if not GRAPH_API_URL:
        return False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{GRAPH_API_URL}/health")
            return r.status_code == 200
    except Exception:
        return False


async def graph_download_cached(entity_id: str, endpoint_key: str) -> bytes:
    """GET /cache/{entity_id}/{endpoint_key} — return raw bytes for file download."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/cache/{entity_id}/{endpoint_key}",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.content
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_resolve_person(ch_officer_id: str) -> str | None:
    """GET /person/by-ch-id/{id} — resolve a CH officer ID to the Neo4j p: ID. Returns None if not found."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/person/by-ch-id/{ch_officer_id}",
                headers=_headers(),
            )
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json().get("person_id")
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_start_enrich(entity_type: str, entity_id: str) -> dict[str, Any]:
    """POST /company/{n}/enrich or /officer/{id}/enrich — start a background enrichment job."""
    _require_config()
    _endpoints = {
        "Company": f"/company/{entity_id}/enrich",
        "Person": f"/officer/{entity_id}/enrich",
    }
    endpoint = _endpoints.get(entity_type)
    if not endpoint:
        raise GraphAPIError(f"Unsupported entity_type for enrichment: {entity_type}")
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"{GRAPH_API_URL}{endpoint}",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_enrich_status(job_id: str) -> dict[str, Any]:
    """GET /enrich/status/{job_id} — poll enrichment job status."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/enrich/status/{job_id}",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_ownership_chain(company_number: str) -> list[dict[str, Any]]:
    """GET /company/{n}/ownership-chain — PSC_CORPORATE chain upward from this company."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/company/{company_number}/ownership-chain",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_company_health(company_number: str) -> dict[str, Any]:
    """GET /company/{n}/health — company health flags for the intelligence panel."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/company/{company_number}/health",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_person_risk(officer_id: str) -> dict[str, Any]:
    """GET /person/{id}/risk-profile — risk level + signals."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/person/{officer_id}/risk-profile",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_person_tenure(officer_id: str) -> dict[str, Any]:
    """GET /person/{id}/tenure-stats — tenure statistics."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/person/{officer_id}/tenure-stats",
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


async def graph_co_located(company_number: str, limit: int = 20) -> list[dict[str, Any]]:
    """GET /company/{n}/co-located — companies at the same address."""
    _require_config()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"{GRAPH_API_URL}/company/{company_number}/co-located",
                params={"limit": limit},
                headers=_headers(),
            )
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise GraphAPIError("Graph API timed out")
    except httpx.HTTPStatusError as e:
        raise GraphAPIError(f"Graph API returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise GraphAPIError(f"Graph API unreachable: {e}")


def _require_config() -> None:
    if not GRAPH_API_URL:
        raise GraphAPIError("GRAPH_API_URL is not configured")
    if not ODL_GRAPH_API_KEY:
        raise GraphAPIError("ODL_GRAPH_API_KEY is not configured")
