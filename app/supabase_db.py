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


def db_select(table: str, filters: dict = None, limit: int = 100000):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in (filters or {}).items()}
    h = _headers()
    
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
    
    if category: params["category"] = f"eq.{category}"
    if freq:
        freq_map = {"Real-time": "(Real-time,Streaming)", "Hourly": "(Hourly)", "Daily": "(Daily)", "Monthly": "(Monthly)", "Annual": "(Annual)"}
        params["update_frequency"] = f"in.{freq_map[freq]}" if freq in freq_map else f"eq.{freq}"
    if access: params["access_methods"] = f"cs.{{{access}}}"
    if q: params["or"] = f"(title.ilike.*{q}*,description.ilike.*{q}*,provider.ilike.*{q}*,category.ilike.*{q}*)"

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
        if r.status_code != 200: break
        chunk = r.json()
        all_res.extend(chunk)
        if len(chunk) < chunk_size: break
        
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


def auth_invite(email: str, data: dict = None, redirect_to: str = None):
    """Generate an invite link via Supabase admin generate_link API.
    Returns the action_link the invitee must click to accept.
    Note: /admin/invite is not available on free plan — generate_link is used instead.
    """
    url = f"{SUPABASE_URL}/auth/v1/admin/generate_link"
    body = {"type": "invite", "email": email}
    if redirect_to:
        body["redirect_to"] = redirect_to
    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    r = httpx.post(url, json=body, headers=headers)
    r.raise_for_status()
    return r.json()
