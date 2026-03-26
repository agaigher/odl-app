"""
Explore module: data access options.
"""
from fasthtml.common import *
from app.auth.middleware import get_user_id
from app.ui.components import module_page_layout


def register(rt):

    @rt("/explore")
    def get_explore(session):
        from app.pages.explore import ExploreChat
        user_email = session.get('user', '')
        return module_page_layout(
            "Explore", "/explore", user_email,
            ExploreChat(),
            session=session, active_module="explore", show_sidebar=False,
        )
