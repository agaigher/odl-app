"""
Organisation settings routes: general, avatar, rename, transfer, delete, billing email, SSO.
"""
import time
from starlette.datastructures import UploadFile
from fasthtml.common import *

from app.auth.middleware import get_user_id
from app.db import db_select, db_patch, db_delete, db_insert, log_audit, storage_upload
from app.ui.components import page_layout


def register(rt):

    @rt("/settings")
    def get_settings(req, session, tab: str = 'general'):
        from app.pages.settings import OrganizationSettings
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        content = OrganizationSettings(user_id, session, tab)
        if "HX-Request" in req.headers:
            return content
        return page_layout("Organization Settings", "/settings", session.get('user'),
                           content, session=session, full_width=True)

    @rt("/settings/avatar", methods=["POST"])
    async def post_settings_avatar(session, avatar_file: UploadFile):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            file_bytes = await avatar_file.read()
            if not file_bytes:
                return RedirectResponse("/settings", status_code=303)
            filename = f"{org_id}/avatar_{int(time.time())}.png"
            public_url = storage_upload("org-avatars", filename, file_bytes, avatar_file.content_type)
            db_patch("organisations", {"avatar_url": public_url}, {"id": org_id})
            log_audit(org_id, user_id, "Updated organization avatar", "organisation", org_id)
            return RedirectResponse("/settings", status_code=303)
        except Exception as e:
            return Div(f"Failed to upload: {str(e)}", cls="error-text", style="margin-top: 8px;")

    @rt("/settings/rename", methods=["POST"])
    def post_settings_rename(session, org_name: str):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            db_patch("organisations", {"name": org_name}, {"id": org_id})
            log_audit(org_id, user_id, f"Renamed organization to '{org_name}'", "organisation", org_id)
            session['force_header_refresh'] = True
            return Div("Organization name updated successfully.", cls="success-text", style="margin-top: 8px;")
        except Exception as e:
            return Div(f"Failed to update name: {e}", cls="error-text", style="margin-top: 8px;")

    @rt("/settings/transfer", methods=["POST"])
    def post_settings_transfer(session, target_user_id: str):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            role = memberships[0].get("role", "member")
            if role != "owner":
                return Div("Only the organization owner can execute transfers.",
                           cls="error-text", style="margin-top: 8px;")
            target = db_select("memberships", {"user_id": target_user_id, "org_id": org_id, "status": "active"})
            if not target:
                return Div("Target user is not an active team member.",
                           cls="error-text", style="margin-top: 8px;")
            db_patch("memberships", {"role": "admin"}, {"user_id": user_id, "org_id": org_id})
            db_patch("memberships", {"role": "owner"}, {"user_id": target_user_id, "org_id": org_id})
            log_audit(org_id, user_id, f"Transferred ownership to user {target_user_id}", "organisation", org_id)
            return RedirectResponse("/settings", status_code=303)
        except Exception as e:
            return Div(f"Transfer failed: {str(e)}", cls="error-text", style="margin-top: 8px;")

    @rt("/settings/delete", methods=["POST"])
    def post_settings_delete(session):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            db_delete("organisations", {"id": org_id})
            return RedirectResponse("/projects", status_code=303)
        except Exception as e:
            return f"Failed to delete organization: {e}", 500

    @rt("/settings/billing", methods=["POST"])
    def post_settings_billing(session, billing_email: str):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            db_patch("organisations", {"billing_email": billing_email}, {"id": org_id})
            log_audit(org_id, user_id, f"Updated billing email to '{billing_email}'", "organisation", org_id)
            return Div("Billing email updated successfully.", cls="success-text", style="margin-top: 8px;")
        except Exception as e:
            return Div(f"Failed to update billing email: {e}", cls="error-text", style="margin-top: 8px;")

    @rt("/settings/sso", methods=["POST"])
    def post_settings_sso(session, domain: str, metadata_url: str, is_active: bool = False):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            db_insert("sso_configurations", {
                "org_id": org_id, "domain": domain,
                "metadata_url": metadata_url, "is_active": is_active,
            })
            log_audit(org_id, user_id, f"Updated SSO configuration (Active: {is_active})", "sso", org_id)
            return Div("SSO configuration saved successfully.", cls="success-text", style="margin-top: 8px;")
        except Exception as e:
            return Div(f"Failed to save SSO config: {e}", cls="error-text", style="margin-top: 8px;")
