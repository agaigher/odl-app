"""
Catalog routes: browsing, search, AI search, dataset detail, favourites.
"""
from fasthtml.common import *
from app.auth.middleware import get_user_id
from app.db import db_select, db_insert, db_delete
from app.ui.components import module_page_layout
from app.pages.catalog import DataCatalog
from app.pages.dataset import DatasetDetail


def register(rt):

    @rt("/catalog")
    def get_catalog(session, q: str = "", category: str = "", access: str = "", freq: str = "",
                    provider: str = "", status: str = "", tags: str = "",
                    page: int = 1, per_page: int = 25):
        user_id = get_user_id(session)
        return module_page_layout("London Database", "/catalog", session.get('user'),
                           DataCatalog(category=category, q=q, user_id=user_id,
                                      access_filter=access, freq_filter=freq,
                                      provider_filter=provider, status_filter=status, tags_filter=tags,
                                       page=page, per_page=per_page),
                           session=session, active_module="catalog", show_sidebar=False, full_width=True)

    @rt("/catalog/search")
    def get_catalog_search(session, q: str = "", category: str = "", access: str = "", freq: str = "",
                           provider: str = "", status: str = "", tags: str = "",
                           page: int = 1, per_page: int = 25):
        from app.pages.catalog import SearchCatalogResults
        user_id = get_user_id(session)
        return SearchCatalogResults(q=q, category=category, user_id=user_id,
                                    access_filter=access, freq_filter=freq,
                                    provider_filter=provider, status_filter=status, tags_filter=tags,
                                    page=page, per_page=per_page)

    @rt("/catalog/ai-search", methods=["POST"])
    def post_ai_search(session, query: str = ""):
        from app.pages.catalog import AiSearchResults
        user_id = get_user_id(session)
        return AiSearchResults(query=query, user_id=user_id)

    @rt("/catalog/{slug}/integration-modal", methods=["GET"])
    def get_integration_modal(slug: str, session):
        from app.pages.catalog import IntegrationModal
        user_id = get_user_id(session)
        if not user_id:
            return Script("window.location.href='/login'")
        project_id = session.get('active_project_id')
        if not project_id:
            return Div("Please select or create an active Project from the Projects tab before managing integrations.",
                       cls="error-text", style="padding:24px;background:#fff;border-radius:8px;")
        try:
            ds = db_select("datasets", {"slug": slug})
            title = ds[0].get("title") if ds else slug
        except Exception:
            title = slug
        return IntegrationModal(slug, title, project_id)

    @rt("/catalog/{slug}/add-btn", methods=["GET"])
    def get_add_btn(slug: str, session):
        from app.pages.catalog import _add_btn
        user_id = get_user_id(session)
        if not user_id:
            return _add_btn(slug, False)
        project_id = session.get('active_project_id')
        if not project_id:
            return _add_btn(slug, False)
        try:
            project_ints = db_select("integrations", {"project_id": project_id})
            project_int_ids = {i["id"] for i in project_ints}
            items = db_select("dataset_integrations", {"dataset_slug": slug})
            is_assigned = any(item["integration_id"] in project_int_ids for item in items)
            return _add_btn(slug, is_assigned)
        except Exception:
            return _add_btn(slug, False)

    @rt("/catalog/{slug}/favourite-modal", methods=["GET"])
    def get_favourite_modal(slug: str, session):
        from app.pages.catalog import FavouriteModal
        user_id = get_user_id(session)
        if not user_id:
            return Script("window.location.href='/login'")
        try:
            ds = db_select("datasets", {"slug": slug})
            title = ds[0].get("title") if ds else slug
        except Exception:
            title = slug
        return FavouriteModal(slug, title, user_id)

    @rt("/catalog/{slug}/fav-btn", methods=["GET"])
    def get_fav_btn(slug: str, session):
        from app.pages.catalog import _fav_btn
        user_id = get_user_id(session)
        if not user_id:
            return _fav_btn(slug, False)
        try:
            items = db_select("favourite_items", {"user_id": user_id, "dataset_slug": slug})
            return _fav_btn(slug, len(items) > 0)
        except Exception:
            return _fav_btn(slug, False)

    @rt("/favourite-lists", methods=["POST"])
    def post_favourite_lists(slug: str, name: str, session):
        from app.pages.catalog import _list_checkbox
        user_id = get_user_id(session)
        if not user_id or not name.strip():
            return ""
        try:
            created = db_insert("favourite_lists", {"user_id": user_id, "name": name.strip()})
            list_id = created[0]["id"]
            db_insert("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
            return _list_checkbox(list_id, slug, True, name.strip())
        except Exception:
            return ""

    @rt("/favourite-lists/{list_id}/toggle", methods=["POST"])
    def post_toggle_list_item(list_id: str, slug: str, session):
        from app.pages.catalog import _list_checkbox
        user_id = get_user_id(session)
        if not user_id:
            return ""
        try:
            existing = db_select("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
            if existing:
                db_delete("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
                in_list = False
            else:
                db_insert("favourite_items", {"list_id": list_id, "user_id": user_id, "dataset_slug": slug})
                in_list = True
            lst = db_select("favourite_lists", {"id": list_id, "user_id": user_id})
            list_name = lst[0]["name"] if lst else "List"
            return _list_checkbox(list_id, slug, in_list, list_name)
        except Exception:
            return ""

    @rt("/favourite-lists/create", methods=["POST"])
    def post_create_fav_list(name: str, session):
        user_id = get_user_id(session)
        if user_id and name.strip():
            try:
                db_insert("favourite_lists", {"user_id": user_id, "name": name.strip()})
                return "ok"
            except Exception:
                return "error"
        return "unauthorized"

    @rt("/favourite-lists/{list_id}/items/{slug}/remove", methods=["POST"])
    def post_remove_fav_item(list_id: str, slug: str, session):
        user_id = get_user_id(session)
        if user_id:
            try:
                db_delete("favourite_items", {"list_id": list_id, "dataset_slug": slug, "user_id": user_id})
            except Exception:
                pass
        return RedirectResponse("/favourites", status_code=303)

    @rt("/favourite-lists/{list_id}/delete", methods=["POST"])
    def post_delete_fav_list(list_id: str, session):
        user_id = get_user_id(session)
        if user_id:
            try:
                db_delete("favourite_items", {"list_id": list_id, "user_id": user_id})
                db_delete("favourite_lists", {"id": list_id, "user_id": user_id})
            except Exception:
                pass
        return RedirectResponse("/favourites", status_code=303)

    @rt("/favourites")
    def get_favourites(session):
        from app.pages.catalog import FavouritesView
        user_id = get_user_id(session)
        return module_page_layout("Favourites", "/favourites", session.get('user'), FavouritesView(user_id=user_id),
                                  session=session, active_module="catalog", show_sidebar=False)

    @rt("/catalog/{slug}")
    def get_dataset(slug: str, session):
        return module_page_layout("Dataset Details", f"/catalog/{slug}", session.get('user'), DatasetDetail(slug, session),
                                  session=session, active_module="catalog", show_sidebar=False)

    @rt("/catalog/{slug}/request-access", methods=["GET"])
    def get_request_access(slug: str, session, type: str = "api"):
        from app.pages.request_access import RequestAccessPage
        return RequestAccessPage(slug=slug, access_type=type, session=session)

    @rt("/catalog/{slug}/request-access", methods=["POST"])
    def post_request_access(slug: str, access_type: str, snowflake_account: str = "", session=None):
        from app.auth.client import get_auth_client
        if not session or not session.get('user'):
            return Div("Not authenticated.", cls="error-text")
        try:
            supabase = get_auth_client()
            user = supabase.get_user(session.get('access_token'))
            user_id = str(user.user.id)
        except Exception:
            return Div("Authentication error. Please log in again.", cls="error-text")
        try:
            if access_type == "snowflake":
                if not snowflake_account:
                    return Div("Snowflake account identifier is required.", cls="error-text")
                db_insert("share_requests", {
                    "user_id": user_id, "dataset_slug": slug,
                    "snowflake_account": snowflake_account, "status": "pending",
                })
                return Div("Request submitted! We'll provision your Snowflake share within 24 hours.", cls="success-text")
            else:
                db_insert("dataset_access", {
                    "user_id": user_id, "dataset_slug": slug,
                    "access_type": "api", "status": "active",
                })
                return Script("window.location.href = '/keys';")
        except Exception as e:
            err = str(e)
            if "duplicate" in err.lower() or "unique" in err.lower():
                return Div("You already have access to this dataset.", cls="success-text")
            return Div(f"Error: {err}", cls="error-text")
