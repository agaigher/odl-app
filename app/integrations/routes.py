"""
Integration routes: list, create, delete, detail, toggle, remove-dataset.
"""
from fasthtml.common import *
from app.auth.middleware import get_user_id
from app.db import db_select, db_insert, db_delete, log_audit
from app.ui.components import page_layout


def register(rt):

    @rt("/integrations")
    def get_integrations(session):
        from app.pages.integrations import IntegrationsView
        user_id = get_user_id(session)
        return page_layout("Data Integrations", "/integrations", session.get('user'),
                           IntegrationsView(user_id=user_id, session=session))

    @rt("/integrations/create", methods=["POST"])
    def post_create_integration(name: str, type: str, session):
        from app.pages.integrations import _integration_row
        user_id = get_user_id(session)
        project_id = session.get('active_project_id')
        if user_id and project_id and name.strip() and type in ("api", "snowflake"):
            try:
                created = db_insert("integrations", {
                    "project_id": project_id, "name": name.strip(), "type": type,
                })
                if created:
                    log_audit(session.get('active_org_id'), user_id,
                              f"Created integration '{name}'", "integration", created[0]["id"])
                    return _integration_row(created[0])
            except Exception:
                pass
        return ""

    @rt("/integrations/{int_id}/delete", methods=["POST"])
    def post_delete_integration(int_id: str, session):
        user_id = get_user_id(session)
        if user_id:
            try:
                db_delete("integrations", {"id": int_id})
                log_audit(session.get('active_org_id'), user_id,
                          f"Deleted integration {int_id}", "integration", int_id)
            except Exception:
                pass
        return ""

    @rt("/integrations/{int_id}")
    def get_integration_detail(int_id: str, session):
        from app.pages.integration_detail import IntegrationDetailView
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login")
        return page_layout("Integration Details", "/integrations", session.get('user'),
                           IntegrationDetailView(integration_id=int_id, user_id=user_id, session=session))

    @rt("/integrations/{int_id}/remove-dataset/{slug}", methods=["POST"])
    def post_int_remove_dataset(int_id: str, slug: str, session):
        user_id = get_user_id(session)
        if user_id:
            try:
                db_delete("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
            except Exception:
                pass
        return ""

    @rt("/integrations/{int_id}/toggle", methods=["POST"])
    def post_toggle_integration(int_id: str, slug: str, session):
        """Toggle a dataset in/out of an integration (used from both catalog and detail views)."""
        from app.pages.catalog import _int_checkbox
        user_id = get_user_id(session)
        if not user_id:
            return ""
        try:
            existing = db_select("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
            if existing:
                db_delete("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
                in_list = False
            else:
                db_insert("dataset_integrations", {"integration_id": int_id, "dataset_slug": slug})
                in_list = True

            ints = db_select("integrations", {"id": int_id})
            int_name = ints[0]["name"] if ints else "Integration"
            return _int_checkbox(int_id, slug, in_list, int_name)
        except Exception:
            return ""
