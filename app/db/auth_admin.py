"""
Supabase Admin auth helpers (invite link generation).
"""
import httpx

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY


def auth_user_exists_for_email(email: str) -> bool:
    """
    Return True if a Supabase Auth user already exists for this email.

    Uses GET /auth/v1/admin/users with the service role. When the service key is
    missing or the request fails, returns False so signup can fall back to
    inspecting the sign_up response (GoTrue may return HTTP 200 for duplicates).
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return False
    e = (email or "").strip().lower()
    if not e:
        return False
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/auth/v1/admin/users",
            params={"per_page": 1, "filter": e},
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
            timeout=15.0,
        )
        r.raise_for_status()
        users = (r.json() or {}).get("users") or []
        return len(users) > 0
    except Exception as ex:
        print(f"auth_user_exists_for_email: {ex}")
        return False


def auth_invite(email: str, data: dict = None, redirect_to: str = None):
    """Generate an invite link via Supabase admin generate_link API."""
    url = f"{SUPABASE_URL}/auth/v1/admin/generate_link"
    body = {"type": "invite", "email": email}
    if redirect_to:
        body["redirect_to"] = redirect_to
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    r = httpx.post(url, json=body, headers=headers)
    r.raise_for_status()
    return r.json()
