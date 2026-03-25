"""
Supabase Auth client singleton.
"""
from supabase_auth import SyncGoTrueClient
from app.config import SUPABASE_URL, SUPABASE_KEY

_client = None


def get_auth_client():
    """Return a configured Supabase GoTrue client, or None if credentials are missing."""
    global _client
    if _client is not None:
        return _client
    if SUPABASE_URL and SUPABASE_KEY:
        _client = SyncGoTrueClient(
            url=f"{SUPABASE_URL}/auth/v1",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        )
    else:
        print("Warning: SUPABASE_URL and SUPABASE_KEY not found in .env. Auth will fail.")
    return _client
