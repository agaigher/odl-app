"""
Team management routes: list, members, invite, role, remove, resend, revoke.
"""
from fasthtml.common import *
from app.auth.middleware import get_user_id
from app.db import db_select, db_insert, db_delete, db_patch, log_audit
from app.ui.components import page_layout


def register(rt):

    @rt("/team")
    def get_team(session):
        from app.pages.team import TeamPage
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        return page_layout("Team", "/team", session.get('user'),
                           TeamPage(user_id=user_id, session=session), session=session)

    @rt("/team/members", methods=["GET"])
    def get_team_members(session):
        from app.pages.team import _team_table_body
        user_id = get_user_id(session)
        if not user_id:
            return ""
        active_org_id = session.get("active_org_id")
        if not active_org_id:
            return ""
        try:
            all_members = db_select("memberships", {"org_id": active_org_id})
            viewer_role = "member"
            for m in all_members:
                if m.get("user_id") == user_id and m.get("status") == "active":
                    viewer_role = m.get("role", "member")
                    break
            projects = db_select("projects", {"org_id": active_org_id})
        except Exception:
            all_members, projects, viewer_role = [], [], "member"
        rows = _team_table_body(all_members, viewer_role, active_org_id, projects)
        return tuple(rows) if isinstance(rows, list) else rows

    @rt("/team/invite", methods=["POST"])
    def post_team_invite(session, invited_email: str, role: str, org_id: str):
        from app.config import APP_URL
        from app.db import auth_invite
        from app.email import send_org_invite
        user_id = get_user_id(session)
        if not user_id:
            return Div("Not authenticated.", cls="error-text")
        if not invited_email:
            return Div("Email address is required.", cls="error-text")
        if role not in ("admin", "project_admin", "member"):
            role = "member"
        try:
            caller_m = db_select("memberships", {"user_id": user_id, "org_id": org_id, "status": "active"})
            if not caller_m or caller_m[0].get("role") not in ("owner", "admin"):
                return Div("You don't have permission to invite members.", cls="error-text")
            if role == "admin" and caller_m[0].get("role") != "owner":
                return Div("Only owners can invite admins.", cls="error-text")
            orgs = db_select("organisations", {"id": org_id})
            org_name = orgs[0]["name"] if orgs else "Organization"
            org_slug = orgs[0].get("slug", "") if orgs else ""
            existing = db_select("memberships", {"org_id": org_id, "invited_email": invited_email})
            if existing:
                return Div("This person already has an invitation or membership.", cls="error-text")
            db_insert("memberships", {
                "org_id": org_id, "invited_email": invited_email,
                "role": role, "status": "pending",
            })
            result = auth_invite(email=invited_email, redirect_to=f"{APP_URL}/invite/accept?org={org_slug}")
            invite_link = result.get("action_link", "")
            email_sent = send_org_invite(
                invited_email=invited_email, org_name=org_name, role=role,
                invite_link=invite_link, invited_by=session.get('user', ''),
            )
            log_audit(org_id, user_id, f"Invited {invited_email} as {role}", "membership", "")
            if email_sent:
                return Div(f"Invitation sent to {invited_email}.", cls="success-text")
            return Div(f"Membership created for {invited_email}. Email delivery not configured — share the invite link manually.",
                       cls="success-text")
        except Exception as e:
            err = str(e)
            if "duplicate key" in err or "unique" in err.lower():
                return Div("That email already has a pending invite or membership.", cls="error-text")
            return Div(f"Error: {err}", cls="error-text")

    @rt("/team/role", methods=["POST"])
    def post_team_role(session, membership_id: str, new_role: str):
        user_id = get_user_id(session)
        if not user_id:
            return ""
        active_org_id = session.get("active_org_id")
        if not active_org_id:
            return ""
        try:
            caller_m = db_select("memberships", {"user_id": user_id, "org_id": active_org_id, "status": "active"})
            if not caller_m or caller_m[0].get("role") not in ("owner", "admin"):
                return ""
            if new_role == "admin" and caller_m[0].get("role") != "owner":
                return ""
            if new_role not in ("admin", "project_admin", "member"):
                return ""
            db_patch("memberships", {"role": new_role}, {"id": membership_id, "org_id": active_org_id})
            log_audit(active_org_id, user_id, f"Changed member role to {new_role}", "membership", membership_id)
            return get_team_members(session)
        except Exception:
            return ""

    @rt("/team/remove", methods=["POST"])
    def post_team_remove(session, membership_id: str):
        user_id = get_user_id(session)
        if not user_id:
            return ""
        active_org_id = session.get("active_org_id")
        if not active_org_id:
            return ""
        try:
            caller_m = db_select("memberships", {"user_id": user_id, "org_id": active_org_id, "status": "active"})
            if not caller_m or caller_m[0].get("role") not in ("owner", "admin"):
                return ""
            target_m = db_select("memberships", {"id": membership_id, "org_id": active_org_id})
            if target_m and target_m[0].get("role") == "owner":
                return ""
            if caller_m[0].get("role") == "admin" and target_m and target_m[0].get("role") == "admin":
                return ""
            db_delete("memberships", {"id": membership_id, "org_id": active_org_id})
            removed_email = target_m[0].get("invited_email", "") if target_m else ""
            log_audit(active_org_id, user_id, f"Removed member {removed_email}", "membership", membership_id)
            return get_team_members(session)
        except Exception:
            return ""

    @rt("/team/resend", methods=["POST"])
    def post_team_resend(session, membership_id: str):
        from app.config import APP_URL
        from app.db import auth_invite
        from app.email import send_org_invite
        user_id = get_user_id(session)
        if not user_id:
            return ""
        active_org_id = session.get("active_org_id")
        if not active_org_id:
            return ""
        try:
            caller_m = db_select("memberships", {"user_id": user_id, "org_id": active_org_id, "status": "active"})
            if not caller_m or caller_m[0].get("role") not in ("owner", "admin"):
                return ""
            target_m = db_select("memberships", {"id": membership_id, "org_id": active_org_id, "status": "pending"})
            if not target_m:
                return ""
            invited_email = target_m[0].get("invited_email", "")
            role = target_m[0].get("role", "member")
            orgs = db_select("organisations", {"id": active_org_id})
            org_name = orgs[0]["name"] if orgs else "Organization"
            org_slug = orgs[0].get("slug", "") if orgs else ""
            result = auth_invite(email=invited_email, redirect_to=f"{APP_URL}/invite/accept?org={org_slug}")
            invite_link = result.get("action_link", "")
            send_org_invite(
                invited_email=invited_email, org_name=org_name, role=role,
                invite_link=invite_link, invited_by=session.get('user', ''),
            )
            log_audit(active_org_id, user_id, f"Resent invite to {invited_email}", "membership", membership_id)
            return get_team_members(session)
        except Exception:
            return ""

    @rt("/team/revoke", methods=["POST"])
    def post_team_revoke(session, membership_id: str):
        user_id = get_user_id(session)
        if not user_id:
            return ""
        active_org_id = session.get("active_org_id")
        if not active_org_id:
            return ""
        try:
            caller_m = db_select("memberships", {"user_id": user_id, "org_id": active_org_id, "status": "active"})
            if not caller_m or caller_m[0].get("role") not in ("owner", "admin"):
                return ""
            target_m = db_select("memberships", {"id": membership_id, "org_id": active_org_id, "status": "pending"})
            if not target_m:
                return ""
            db_delete("memberships", {"id": membership_id, "org_id": active_org_id})
            revoked_email = target_m[0].get("invited_email", "")
            log_audit(active_org_id, user_id, f"Revoked invite for {revoked_email}", "membership", membership_id)
            return get_team_members(session)
        except Exception:
            return ""
