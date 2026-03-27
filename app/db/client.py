"""
Core Supabase PostgREST operations: insert, select, patch, delete.
"""
import httpx
import re
from datetime import datetime

from app.auth.confirmation import auth_user_json_may_use_app
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


def _matches_keywords(dataset, keywords):
    if not keywords:
        return True
    hay = " ".join([
        str(dataset.get("title") or ""),
        str(dataset.get("description") or ""),
        str(dataset.get("provider") or ""),
    ]).lower()
    return any(k.lower() in hay for k in keywords if k)


def _parse_iso_datetime(value):
    if not value or not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _extract_size_mb(dataset):
    direct_mb_keys = (
        "size_mb",
        "dataset_size_mb",
        "file_size_mb",
        "download_size_mb",
    )
    for key in direct_mb_keys:
        value = dataset.get(key)
        if isinstance(value, (int, float)) and value >= 0:
            return float(value)

    bytes_keys = (
        "size_bytes",
        "dataset_size_bytes",
        "file_size_bytes",
        "bytes",
    )
    for key in bytes_keys:
        value = dataset.get(key)
        if isinstance(value, (int, float)) and value >= 0:
            return float(value) / (1024 * 1024)

    text = f'{dataset.get("description") or ""} {dataset.get("long_description") or ""}'.lower()
    match = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(gb|gib|mb|mib|kb|kib|bytes?|b)\b", text)
    if not match:
        return None
    amount = float(match.group(1).replace(",", ""))
    unit = match.group(2)
    if unit in ("gb", "gib"):
        return amount * 1024
    if unit in ("mb", "mib"):
        return amount
    if unit in ("kb", "kib"):
        return amount / 1024
    return amount / (1024 * 1024)


def _extract_sort_datetime(dataset):
    for key in ("updated_at", "last_updated", "modified_at", "created_at"):
        parsed = _parse_iso_datetime(dataset.get(key))
        if parsed is not None:
            return parsed
    return datetime.min


def _sort_datasets(rows, sort):
    sort_key = (sort or "recent").strip().lower()
    decorated = [
        {
            "row": d,
            "title": str(d.get("title") or d.get("slug") or "").lower(),
            "size_mb": _extract_size_mb(d),
            "row_est": _extract_row_estimate(d),
            "dt": _extract_sort_datetime(d),
        }
        for d in rows
    ]

    if sort_key == "name_asc":
        return [i["row"] for i in sorted(decorated, key=lambda i: i["title"])]
    if sort_key == "name_desc":
        return [i["row"] for i in sorted(decorated, key=lambda i: i["title"], reverse=True)]
    if sort_key == "size_desc":
        return [i["row"] for i in sorted(decorated, key=lambda i: (i["size_mb"] is None, -(i["size_mb"] or 0.0), i["title"]))]
    if sort_key == "size_asc":
        return [i["row"] for i in sorted(decorated, key=lambda i: (i["size_mb"] is None, (i["size_mb"] or 0.0), i["title"]))]
    if sort_key == "rows_desc":
        return [i["row"] for i in sorted(decorated, key=lambda i: (i["row_est"] is None, -(i["row_est"] or 0), i["title"]))]
    if sort_key == "rows_asc":
        return [i["row"] for i in sorted(decorated, key=lambda i: (i["row_est"] is None, (i["row_est"] or 0), i["title"]))]
    return [i["row"] for i in sorted(decorated, key=lambda i: (i["dt"], i["title"]), reverse=True)]


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
                           provider="", status="", tags="", updated_after="", size="", keywords="", sort="recent",
                           slug_in=None):
    url = f"{SUPABASE_URL}/rest/v1/datasets"
    params = {}

    if slug_in is not None:
        slug_in = [s for s in slug_in if s]
        if not slug_in:
            return [], 0
        params["slug"] = _in_values(slug_in)

    categories = _split_csv(category)
    freqs = _split_csv(freq)
    access_methods = _split_csv(access)
    providers = _split_csv(provider)
    statuses = _split_csv(status)
    tags_list = _split_csv(tags)
    keyword_list = _split_csv(keywords)[:10]

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

    sort_key = (sort or "recent").strip().lower()
    requires_full_scan = bool(size or keyword_list or sort_key in {"size_desc", "size_asc", "rows_desc", "rows_asc"})

    if requires_full_scan:
        rows = _fetch_all(url, params=params, limit=12000)
        filtered = [
            d for d in rows
            if _matches_size_bucket(d, size) and _matches_keywords(d, keyword_list)
        ]
        filtered = _sort_datasets(filtered, sort_key)
        total = len(filtered)
        offset = (page - 1) * per_page
        return filtered[offset: offset + per_page], total

    order_map = {
        "recent": "created_at.desc",
        "name_asc": "title.asc",
        "name_desc": "title.desc",
    }
    params["order"] = order_map.get(sort_key, "created_at.desc")

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
        data = r.json()
        if not auth_user_json_may_use_app(data):
            return None
        return data.get("id")
    except Exception as e:
        print(f"Error fetching user ID: {e}")
        return None
