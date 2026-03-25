"""
Core Supabase PostgREST operations: insert, select, patch, delete.
"""
import httpx

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY


def _headers():
    return {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def db_insert(table: str, data: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = httpx.post(url, json=data, headers=_headers())
    r.raise_for_status()
    return r.json()


def db_select(table: str, filters: dict = None, limit: int = 1000, order: str = None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {}
    for k, v in (filters or {}).items():
        if isinstance(v, (list, tuple)):
            if not v:
                return []
            vals = ",".join([str(x) for x in v])
            params[k] = f"in.({vals})"
        else:
            params[k] = f"eq.{v}"
    if order:
        params["order"] = order

    h = _headers()
    if limit <= 1000:
        h["Range-Unit"] = "items"
        h["Range"] = f"0-{limit-1}"
        r = httpx.get(url, params=params, headers=h)
        r.raise_for_status()
        return r.json()

    all_results = []
    chunk_size = 1000
    for offset in range(0, limit, chunk_size):
        end = min(offset + chunk_size - 1, limit - 1)
        h["Range-Unit"] = "items"
        h["Range"] = f"{offset}-{end}"
        r = httpx.get(url, params=params, headers=h)
        r.raise_for_status()
        chunk = r.json()
        all_results.extend(chunk)
        if len(chunk) < chunk_size:
            break
    return all_results


def get_datasets_paginated(category="", q="", access="", freq="", page=1, per_page=25):
    url = f"{SUPABASE_URL}/rest/v1/datasets"
    params = {}

    if category:
        params["category"] = f"eq.{category}"
    if freq:
        freq_map = {
            "Real-time": "(Real-time,Streaming)",
            "Hourly": "(Hourly)",
            "Daily": "(Daily)",
            "Monthly": "(Monthly)",
            "Annual": "(Annual)",
        }
        params["update_frequency"] = f"in.{freq_map[freq]}" if freq in freq_map else f"eq.{freq}"
    if access:
        params["access_methods"] = f"cs.{{{access}}}"
    if q:
        params["or"] = f"(title.ilike.*{q}*,description.ilike.*{q}*,provider.ilike.*{q}*,category.ilike.*{q}*)"

    offset = (page - 1) * per_page
    h = _headers()
    h["Range-Unit"] = "items"
    h["Range"] = f"{offset}-{offset + per_page - 1}"
    h["Prefer"] = "count=exact"

    r = httpx.get(url, params=params, headers=h)
    r.raise_for_status()

    cr = r.headers.get("Content-Range", "")
    total = int(cr.split("/")[-1]) if "/" in cr else len(r.json())
    return r.json(), total


def get_category_counts():
    url = f"{SUPABASE_URL}/rest/v1/datasets"
    h = _headers()
    params = {"select": "category"}
    all_res = []
    chunk_size = 1000
    for offset in range(0, 50000, chunk_size):
        h["Range-Unit"] = "items"
        h["Range"] = f"{offset}-{offset + chunk_size - 1}"
        r = httpx.get(url, params=params, headers=h)
        if r.status_code != 200:
            break
        chunk = r.json()
        all_res.extend(chunk)
        if len(chunk) < chunk_size:
            break
    counts = {}
    for d in all_res:
        c = d.get("category") or "Other"
        counts[c] = counts.get(c, 0) + 1
    return counts, len(all_res)


def db_delete(table: str, filters: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in filters.items()}
    h = _headers()
    h["Prefer"] = "return=minimal"
    r = httpx.delete(url, params=params, headers=h)
    r.raise_for_status()


def db_patch(table: str, data: dict, filters: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in filters.items()}
    h = _headers()
    h["Prefer"] = "return=minimal"
    r = httpx.patch(url, json=data, params=params, headers=h)
    r.raise_for_status()


def log_audit(org_id: str, actor_id: str, action: str, resource_type: str = None, resource_id: str = None):
    import threading

    def _run():
        try:
            db_insert("audit_logs", {
                "org_id": org_id,
                "actor_id": actor_id,
                "action": action,
                "resource_id": resource_id,
                "resource_type": resource_type,
            })
        except Exception as e:
            print(f"Audit Log Error: {e}")

    threading.Thread(target=_run).start()


def get_user_id_from_session(session):
    """Retrieve user ID from Supabase auth using the access_token in session."""
    if not session or not session.get("access_token"):
        return None
    try:
        url = f"{SUPABASE_URL}/auth/v1/user"
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {session.get('access_token')}",
        }
        r = httpx.get(url, headers=headers)
        r.raise_for_status()
        return r.json().get("id")
    except Exception as e:
        print(f"Error fetching user ID: {e}")
        return None
