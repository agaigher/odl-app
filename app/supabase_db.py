"""
Backward-compatible shim — re-exports from the new app.db package.

Existing app/pages/*.py files import from here; this avoids a mass
find-and-replace and lets us migrate page files incrementally.
"""
from app.db.client import (
    db_insert,
    db_select,
    db_patch,
    db_delete,
    get_datasets_paginated,
    get_category_counts,
    log_audit,
    get_user_id_from_session,
    _headers,
)
from app.db.storage import storage_upload
from app.db.auth_admin import auth_invite
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

SERVICE_KEY = SUPABASE_SERVICE_KEY
