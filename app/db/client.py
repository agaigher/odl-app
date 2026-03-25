"""
Core Supabase PostgREST operations: insert, select, patch, delete.
"""
import httpx
import re

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


def _split_csv(raw):
    if not raw:
        return []
    return [v.strip() for v in str(raw).split(",") if v.strip()]


def _in_values(values):
    escaped = [f'"{v.replace(chr(34), r"\"")}"' for v in values]
    return "in.(" + ",".join(escaped) + ")"


def _extract_row_estimate(dataset):
    for key in ("row_count", "rows", "record_count", "dataset_size"):
        v = dataset.get(key)
        if isinstance(v, (int, float)) and v >= 0:
            return int(v)

    text = f'{dataset.get("description") or ""} {dataset.get("long_description") or ""}'.lower()
    pattern = re.compile(
        r'(\d[\d,]*(?:\.\d+)?)\s*(\+)?\s*(billion|million|thousand|bn|m|k)?\s*'
        r'(records?|rows?|entries?|transactions?|observations?|titles?|companies?)?'
    )
    best = None
    for num, plus, unit, noun in pattern.findall(text):
        if not noun and not unit:
            continue
        base = float(num.replace(",", ""))
        mult = 1
        u = (unit or "").lower()
        if u in ("k", "thousand"):
            mult = 1_000
        elif u in ("m", "million"):
            mult = 1_000_000
        elif u in ("bn", "billion"):
            mult = 1_000_000_000
        val = int(base * mult)
        if plus:
            val += 1
        if best is None or val > best:
            best = val
    return best


def _matches_size_bucket(dataset, size_bucket):
    est = _extract_row_estimate(dataset)
    if est is None:
        return False
    if size_bucket == "le_1k":
        return est <= 1_000
    if size_bucket == "le_10k":
        return est <= 10_000
    if size_bucket == "le_100k":
        return est <= 100_000
    if size_bucket == "le_1m":
        return est <= 1_000_000
    if size_bucket == "le_10m":
        return est <= 10_000_000
    if size_bucket == "le_100m":
        return est <= 100_000_000
    if size_bucket == "gt_100m":
        return est > 100_000_000
    return True


def _fetch_all(url, params, limit=10000):
    h = _headers()
    all_rows = []
    chunk_size = 1000
    for offset in range(0, limit, chunk_size):
        h["Range-Unit"] = "items"
        h["Range"] = f"{offset}-{offset + chunk_size - 1}"
        r = httpx.get(url, params=params, headers=h)
        r.raise_for_status()
        chunk = r.json()
        all_rows.extend(chunk)
        if len(chunk) < chunk_size:
            break
    return all_rows


def get_datasets_paginated(category="", q="", access="", freq="", page=1, per_page=25,
                           provider="", status="", tags="", updated_after="", size=""):
    url = f"{SUPABASE_URL}/rest/v1/datasets"
    params = {}

    categories = _split_csv(category)
    freqs = _split_csv(freq)
    access_methods = _split_csv(access)
    providers = _split_csv(provider)
    statuses = _split_csv(status)
    tags_list = _split_csv(tags)

    if categories:
        if len(categories) == 1:
            params["category"] = f"eq.{categories[0]}"
        else:
            params["category"] = _in_values(categories)

    if freqs:
        freq_map = {
            "Real-time": ["Real-time", "Streaming"],
            "Hourly": ["Hourly"],
            "Daily": ["Daily"],
            "Weekly": ["Weekly"],
            "Monthly": ["Monthly"],
            "Quarterly": ["Quarterly"],
            "Yearly": ["Annual"],
            "Less than once a year": ["Irregular", "One-off"],
        }
        expanded = []
        for f in freqs:
            expanded.extend(freq_map.get(f, [f]))
        expanded = sorted(set(expanded))
        if len(expanded) == 1:
            params["update_frequency"] = f"eq.{expanded[0]}"
        else:
            params["update_frequency"] = _in_values(expanded)

    if access_methods:
        if len(access_methods) == 1:
            params["access_methods"] = f"cs.{{{access_methods[0]}}}"
        else:
            params["access_methods"] = "ov.{" + ",".join(access_methods) + "}"

    if providers:
        if len(providers) == 1:
            params["provider"] = f"eq.{providers[0]}"
        else:
            params["provider"] = _in_values(providers)

    if statuses:
        if len(statuses) == 1:
            params["status"] = f"eq.{statuses[0]}"
        else:
            params["status"] = _in_values(statuses)

    if tags_list:
        if len(tags_list) == 1:
            params["tags"] = f"cs.{{{tags_list[0]}}}"
        else:
            params["tags"] = "ov.{" + ",".join(tags_list) + "}"
    if updated_after:
        params["created_at"] = f"gte.{updated_after}"

    if q:
        params["or"] = f"(title.ilike.*{q}*,description.ilike.*{q}*,provider.ilike.*{q}*,category.ilike.*{q}*)"

    if size:
        rows = _fetch_all(url, params=params, limit=12000)
        filtered = [d for d in rows if _matches_size_bucket(d, size)]
        total = len(filtered)
        offset = (page - 1) * per_page
        return filtered[offset: offset + per_page], total

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
