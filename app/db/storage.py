"""
Supabase Storage helper.
"""
import httpx

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY


def storage_upload(bucket: str, path: str, file_bytes: bytes, content_type: str):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    h = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    r = httpx.post(url, content=file_bytes, headers=h)
    r.raise_for_status()
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
