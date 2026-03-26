"""
Supabase REST helpers — thin wrapper over PostgREST.

All database access goes through the functions exported here.
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
from app.db.auth_admin import auth_invite, auth_user_exists_for_email

__all__ = [
    "db_insert",
    "db_select",
    "db_patch",
    "db_delete",
    "get_datasets_paginated",
    "get_category_counts",
    "log_audit",
    "get_user_id_from_session",
    "storage_upload",
    "auth_invite",
    "auth_user_exists_for_email",
]
