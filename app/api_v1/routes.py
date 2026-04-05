"""
Public REST API v1: /api/v1/query

Validates the API key and billing via Supabase, then proxies the query
to odl-api (running on Mac Mini / locally) which executes against DuckDB.
"""
import json
import httpx
from starlette.responses import Response

from app.db import db_select, db_patch
from app.config import ODL_API_URL, ODL_GRAPH_API_URL


def register(rt):

    @rt("/api/v1/query", methods=["POST"])
    async def api_v1_query(req):
        auth_header = req.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response('{"error": "Unauthorized"}', status_code=401, media_type="application/json")

        api_key = auth_header.split(" ")[1]

        try:
            ints = db_select("integrations", {"id": api_key, "type": "api"})
            if not ints:
                return Response('{"error": "Invalid or revoked API Key"}',
                                status_code=403, media_type="application/json")

            project_id = ints[0]["project_id"]

            projects = db_select("projects", {"id": project_id})
            if not projects:
                return Response('{"error": "Project not found"}',
                                status_code=404, media_type="application/json")
            org_id = projects[0]["org_id"]

            orgs = db_select("organisations", {"id": org_id})
            if not orgs:
                return Response('{"error": "Organisation not found"}',
                                status_code=404, media_type="application/json")

            credit_balance = orgs[0].get("credit_balance", 0)
            if credit_balance <= 0:
                return Response(
                    '{"error": "Payment Required. Credit balance is 0. Top up at app.opendata.london/billing"}',
                    status_code=402, media_type="application/json",
                )

            try:
                body = await req.json()
                sql_query = body.get("query")
                dataset_slug = body.get("dataset")
            except Exception:
                return Response('{"error": "Invalid JSON payload. Expected {query: str, dataset: str}"}',
                                status_code=400, media_type="application/json")

            if dataset_slug:
                has_access = db_select("dataset_integrations", {"integration_id": api_key, "dataset_slug": dataset_slug})
                if not has_access:
                    return Response('{"error": "API Key does not have access to this dataset."}',
                                    status_code=403, media_type="application/json")

            # Map dataset slug to odl-api endpoint path (DuckDB-backed datasets)
            DATASET_ROUTES = {
                "london-air-quality": "/v1/datasets/air-quality/readings",
            }

            # Graph datasets route to ODL Graph API (Neo4j + Postgres)
            GRAPH_DATASET_ROUTES = {
                "uk-companies-house": True,
            }

            if dataset_slug in GRAPH_DATASET_ROUTES:
                # Graph API: pass the full request body through and forward to the graph service.
                # The caller specifies an "endpoint" key in the body (e.g. "search", "expand").
                graph_endpoint = body.get("endpoint", "search")
                graph_method = body.get("method", "POST").upper()
                graph_params = body.get("params", {})
                graph_payload = body.get("payload", {})
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        if graph_method == "GET":
                            odl_response = await client.get(
                                f"{ODL_GRAPH_API_URL}/{graph_endpoint}",
                                params=graph_params,
                                headers={"X-API-Key": api_key},
                            )
                        else:
                            odl_response = await client.post(
                                f"{ODL_GRAPH_API_URL}/{graph_endpoint}",
                                json=graph_payload,
                                params=graph_params,
                                headers={"X-API-Key": api_key},
                            )
                except httpx.ConnectError:
                    return Response(
                        '{"error": "Graph service unavailable. Please try again later."}',
                        status_code=503, media_type="application/json",
                    )
            else:
                api_path = DATASET_ROUTES.get(dataset_slug or "")
                if not api_path:
                    return Response(
                        json.dumps({"error": f"Dataset '{dataset_slug}' is not available via API yet."}),
                        status_code=404, media_type="application/json",
                    )

                # Forward query params from the request body to odl-api as query string params
                query_params = body.get("params", {})

                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        odl_response = await client.get(
                            f"{ODL_API_URL}{api_path}",
                            params=query_params,
                            headers={"X-API-Key": api_key},
                        )
                except httpx.ConnectError:
                    return Response(
                        '{"error": "Data service unavailable. Please try again later."}',
                        status_code=503, media_type="application/json",
                    )

            if odl_response.status_code != 200:
                return Response(odl_response.text, status_code=odl_response.status_code,
                                media_type="application/json")

            new_balance = credit_balance - 1
            db_patch("organisations", {"credit_balance": new_balance}, {"id": org_id})

            result = odl_response.json()
            return Response(
                json.dumps({"status": "success", "credits_remaining": new_balance, **result}),
                status_code=200, media_type="application/json",
            )

        except Exception as e:
            print("API V1 ERROR:", e)
            return Response('{"error": "Internal Server Error"}',
                            status_code=500, media_type="application/json")
