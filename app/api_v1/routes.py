"""
Public REST API v1: /api/v1/query
"""
import json
import asyncio
from starlette.responses import Response

from app.db import db_select, db_patch


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

            await asyncio.sleep(0.3)
            mock_data = [{"example": "response", "source": dataset_slug or "global"}]

            new_balance = credit_balance - 1
            db_patch("organisations", {"credit_balance": new_balance}, {"id": org_id})

            return Response(
                json.dumps({"status": "success", "credits_remaining": new_balance, "data": mock_data}),
                status_code=200, media_type="application/json",
            )

        except Exception as e:
            print("API V1 ERROR:", e)
            return Response('{"error": "Internal Server Error"}',
                            status_code=500, media_type="application/json")
