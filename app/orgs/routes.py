"""
Organisation routes: list, switch, open, detail, create.
"""
import httpx
from fasthtml.common import *

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from app.auth.middleware import get_user_id
from app.db import db_select, db_insert, log_audit
from app.ui.components import page_layout
from app.pages.create_org import CreateOrgPage
from app.pages.organisations import OrganisationsPage


def register(rt):

    @rt("/create-org", methods=["GET"])
    def get_create_org(session):
        if not session.get('user'):
            return RedirectResponse('/login', status_code=303)
        return CreateOrgPage()

    @rt("/create-org", methods=["POST"])
    def post_create_org(org_name: str, slug: str, session):
        user_id = get_user_id(session)
        if not user_id:
            return Div("Not authenticated.", cls="error-text")
        if not org_name or not slug:
            return Div("Organisation name and slug are required.", cls="error-text")
        slug = slug.lower().strip().replace(" ", "-")
        try:
            orgs = db_insert("organisations", {
                "name": org_name, "slug": slug, "created_by": user_id,
            })
            if not orgs:
                raise Exception("Failed to create organisation record.")
            org_id = orgs[0]["id"]
            db_insert("memberships", {
                "org_id": org_id, "user_id": user_id, "role": "owner", "status": "active",
            })
            session['active_org_id'] = org_id
            session['force_header_refresh'] = True
            log_audit(org_id, user_id, "Organization created", "organisation", org_id)
            return Script("window.location.href = '/projects';")
        except Exception as e:
            err = str(e)
            if "duplicate key" in err or "unique" in err.lower():
                return Div("That slug is already taken. Choose a different one.", cls="error-text")
            return Div(f"Error: {err}", cls="error-text")

    @rt("/org/switch", methods=["POST"])
    def post_org_switch(session, org_id: str):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            m = db_select("memberships", {"user_id": user_id, "org_id": org_id, "status": "active"})
            if not m:
                return "Unauthorized", 403
            session['active_org_id'] = org_id
            session.pop('active_project_id', None)
            session['force_header_refresh'] = True
            return Script("window.location.href = '/projects';")
        except Exception:
            return "Error", 500

    @rt("/organisations")
    def get_organisations(session):
        user_id = get_user_id(session)
        user = session.get('user')
        if not user_id:
            return RedirectResponse("/login", status_code=303)

        m = db_select("memberships", {"user_id": user_id, "status": "active"})
        org_ids = [row["org_id"] for row in m]

        orgs = []
        if org_ids:
            try:
                ids_str = ",".join([str(i) for i in org_ids])
                url = f"{SUPABASE_URL}/rest/v1/organisations"
                headers = {
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                }
                r = httpx.get(url, params={"id": f"in.({ids_str})"}, headers=headers)
                r.raise_for_status()
                orgs = r.json()
            except Exception as e:
                print(f"Error fetching orgs: {e}")

            for org in orgs:
                oid = org.get("id")
                if not oid:
                    org["member_count"] = org["project_count"] = 0
                    continue
                try:
                    members = db_select("memberships", {"org_id": oid, "status": "active"})
                    projs = db_select("projects", {"org_id": oid})
                    org["member_count"] = len(members or [])
                    org["project_count"] = len(projs or [])
                except Exception:
                    org["member_count"] = org["project_count"] = 0

        return page_layout("Organizations", "/organisations", user, OrganisationsPage(orgs), session=session)

    @rt("/org/open/{slug}")
    def get_org_open_and_projects(slug: str, session):
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        orgs = db_select("organisations", {"slug": slug})
        if not orgs:
            return RedirectResponse("/organisations", status_code=303)
        org = orgs[0]
        m = db_select("memberships", {"user_id": user_id, "org_id": org["id"], "status": "active"})
        if not m:
            return RedirectResponse("/organisations", status_code=303)
        session["active_org_id"] = org["id"]
        session.pop("active_project_id", None)
        session["force_header_refresh"] = True
        return RedirectResponse("/projects", status_code=303)

    @rt("/org/{slug}")
    def get_org(slug: str, session):
        from app.pages.org_dashboard import OrgDashboard
        user = session.get('user')
        orgs = db_select("organisations", {"slug": slug})
        if not orgs:
            return "Organization not found", 404
        org = orgs[0]
        session['active_org_id'] = org['id']
        return page_layout(f"{org['name']} Dashboard", f"/org/{slug}", user, OrgDashboard(org), session=session)
