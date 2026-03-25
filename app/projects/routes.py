"""
Project routes: list, create, select.
"""
from fasthtml.common import *
from app.auth.middleware import get_user_id
from app.db import db_insert, log_audit
from app.ui.components import page_layout


def register(rt):

    @rt("/projects/create", methods=["POST"])
    def post_create_project(name: str, org_id: str, session):
        user_id = get_user_id(session)
        if not user_id:
            return "unauthorized"
        try:
            new_p = db_insert("projects", {"org_id": org_id, "name": name.strip()})
            p_id = new_p[0]["id"]
            db_insert("project_members", {"project_id": p_id, "user_id": user_id, "role": "admin"})
            session['active_project_id'] = p_id
            log_audit(org_id, user_id, f"Created project '{name}'", "project", p_id)
            session['force_header_refresh'] = True
            return "ok"
        except Exception:
            return "error"

    @rt("/projects/{p_id}/select", methods=["GET"])
    def get_select_project(p_id: str, session):
        session["active_project_id"] = p_id
        session["force_header_refresh"] = True
        return RedirectResponse("/dashboard", status_code=303)

    @rt("/projects")
    def get_projects(session):
        from app.pages.projects import ProjectsDashboard
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        return page_layout("Projects", "/projects", session.get('user'),
                           ProjectsDashboard(user_id=user_id, session=session), session=session)
