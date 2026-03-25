"""
Supabase Admin auth helpers (invite link generation).
"""
import httpx

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY


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
