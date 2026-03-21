import os
import httpx

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def _headers():
    return {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def db_insert(table: str, data: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = httpx.post(url, json=data, headers=_headers())
    r.raise_for_status()
    return r.json()


def db_select(table: str, filters: dict = None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in (filters or {}).items()}
    r = httpx.get(url, params=params, headers=_headers())
    r.raise_for_status()
    return r.json()
