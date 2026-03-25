"""
Backward-compatible shim — re-exports from the new app.ui package.

Existing app/pages/*.py files import from here.
"""
from app.ui.components import (
    page_layout,
    odl_navbar,
    odl_sidebar,
    icon_svg,
    IC,
    OrgSwitcher,
    ProjectSwitcher,
)
