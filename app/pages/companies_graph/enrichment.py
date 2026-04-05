"""
Enrichment panel components (Sprint 3 & 4).

Company enrichment: Overview | Officers | PSC | Filings | Charges | More
Officer enrichment: Overview | Appointments | Disqualifications
"""
from __future__ import annotations

import json

from fasthtml.common import (
    A, Button, Div, Li, NotStr, P, Script, Span,
    Table, Tbody, Td, Th, Thead, Tr, Ul, FT,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _tab_panel(tabs: list[tuple[str, str, FT]], merge_script: FT) -> FT:
    """Render a tabbed panel given [(slug, label, content), ...]."""
    tab_buttons = Ul(
        *[Li(
            Button(
                label,
                cls=f"enrich-tab__btn{'  enrich-tab__btn--active' if i == 0 else ''}",
                onclick=f"showEnrichTab('{slug}')",
                id=f"enrich-tab-btn-{slug}",
            ),
            cls="enrich-tab__item",
        ) for i, (slug, label, _) in enumerate(tabs)],
        cls="enrich-tab__list",
    )
    tab_panes = Div(
        *[Div(
            content,
            id=f"enrich-tab-{slug}",
            cls=f"enrich-tab__pane{'  enrich-tab__pane--active' if i == 0 else ''}",
        ) for i, (slug, _, content) in enumerate(tabs)],
        cls="enrich-tab__panes",
    )
    return Div(tab_buttons, tab_panes, merge_script, id="enrichment-panel", cls="enrichment-panel")


# ---------------------------------------------------------------------------
# State divs
# ---------------------------------------------------------------------------

def enrichment_spinner(job_id: str) -> FT:
    """Spinner div — polls every 2s until job completes."""
    return Div(
        Div(cls="enrich-spinner"),
        P("Fetching Companies House data\u2026", cls="enrich-spinner__label"),
        id="enrichment-panel",
        cls="enrichment-panel enrichment-panel--loading",
        hx_get=f"/companies-graph/enrich/status/{job_id}",
        hx_trigger="every 2s",
        hx_target="#enrichment-panel",
        hx_swap="outerHTML",
    )


def enrichment_error(message: str) -> FT:
    return Div(
        P(f"Enrichment failed: {message}", cls="enrich-error"),
        id="enrichment-panel",
        cls="enrichment-panel enrichment-panel--error",
    )


# ---------------------------------------------------------------------------
# Company enrichment panel
# ---------------------------------------------------------------------------

def enrichment_panel(result: dict, company_number: str) -> FT:
    payloads = result.get("payloads", {})
    graph_elements = result.get("graph_elements", [])

    tabs = [
        ("overview", "Overview",  _company_tab_overview(payloads.get("profile", {}), payloads.get("registered-office", {}))),
        ("officers", "Officers",  _company_tab_officers(payloads.get("officers", {}).get("items", []), company_number)),
        ("psc",      "PSC",       _company_tab_psc(payloads.get("pscs", {}).get("items", []), company_number)),
        ("filings",  "Filings",   _company_tab_filings(payloads.get("filings", {}).get("items", []))),
        ("charges",  "Charges",   _company_tab_charges(payloads.get("charges", {}).get("items", []))),
        ("more",     "More \u25be", _company_tab_more(company_number, result)),
    ]

    merge_script = Script(
        f"if(typeof mergeElements==='function'){{mergeElements({json.dumps(graph_elements)})}};"
        f"setEnrichedNode('c_{company_number}')",
        type="text/javascript",
    ) if graph_elements else Script(
        f"setEnrichedNode('c_{company_number}')",
        type="text/javascript",
    )

    return _tab_panel(tabs, merge_script)


def _company_tab_overview(profile: dict, office: dict) -> FT:
    if not profile:
        return P("No data available.", cls="enrich-empty")
    fields = [
        ("Status",       profile.get("company_status")),
        ("Type",         profile.get("type")),
        ("Incorporated", profile.get("date_of_creation")),
        ("Dissolved",    profile.get("date_of_cessation")),
        ("SIC codes",    ", ".join(profile.get("sic_codes", []))),
    ]
    addr = office or profile.get("registered_office_address") or {}
    addr_str = ", ".join(p for p in [
        addr.get("premises", ""), addr.get("address_line_1", ""),
        addr.get("address_line_2", ""), addr.get("locality", ""),
        addr.get("postal_code", ""),
    ] if p)
    if addr_str:
        fields.append(("Address", addr_str))
    ch_number = profile.get("company_number", "")
    rows = [
        Tr(Th(k, cls="graph-sidebar__th"), Td(v or "\u2014", cls="graph-sidebar__td"))
        for k, v in fields if v
    ]
    link = A(
        "View on Companies House \u2197",
        href=f"https://find-and-update.company-information.service.gov.uk/company/{ch_number}",
        target="_blank",
        cls="enrich-ch-link",
    ) if ch_number else Div()
    return Div(Table(*rows, cls="graph-sidebar__table") if rows else Div(), link)


def _company_tab_officers(items: list, company_number: str) -> FT:
    if not items:
        return P("No officers found.", cls="enrich-empty")

    def _row(item: dict) -> FT:
        links = item.get("links", {})
        officer_path = links.get("officer", {}).get("appointments", "")
        parts = [p for p in officer_path.strip("/").split("/") if p]
        officer_id = parts[1] if len(parts) >= 3 else ""
        name = item.get("name", "\u2014")
        name_cell = (
            Button(name, cls="enrich-officer-link",
                   onclick=f"fetchDetail('Person', '{officer_id}')")
            if officer_id else Span(name)
        )
        is_active = not bool(item.get("resigned_on"))
        badge = Span("Active", cls="enrich-badge enrich-badge--active") if is_active else Span("Resigned", cls="enrich-badge enrich-badge--resigned")
        return Tr(
            Td(name_cell, cls="graph-sidebar__td"),
            Td(item.get("officer_role", "\u2014"), cls="graph-sidebar__td"),
            Td(item.get("appointed_on", "\u2014"), cls="graph-sidebar__td"),
            Td(item.get("resigned_on", "\u2014"), cls="graph-sidebar__td"),
            Td(badge, cls="graph-sidebar__td"),
        )

    active = [i for i in items if not i.get("resigned_on")]
    resigned = [i for i in items if i.get("resigned_on")]
    return Div(Table(
        Thead(Tr(
            Th("Name", cls="graph-sidebar__th"), Th("Role", cls="graph-sidebar__th"),
            Th("Appointed", cls="graph-sidebar__th"), Th("Resigned", cls="graph-sidebar__th"),
            Th("Status", cls="graph-sidebar__th"),
        )),
        Tbody(*[_row(i) for i in active + resigned]),
        cls="graph-sidebar__table enrich-table",
    ))


def _company_tab_psc(items: list, company_number: str) -> FT:
    if not items:
        return P("No persons with significant control found.", cls="enrich-empty")

    def _row(item: dict) -> FT:
        ne = item.get("name_elements") or {}
        full_name = " ".join(filter(None, [
            ne.get("title"), ne.get("forename"),
            ne.get("other_forenames"), ne.get("surname"),
        ])).strip() or item.get("name", "\u2014")
        noc = item.get("natures_of_control") or []
        is_active = not bool(item.get("ceased_on"))
        badge = Span("Active", cls="enrich-badge enrich-badge--active") if is_active else Span("Ceased", cls="enrich-badge enrich-badge--resigned")
        return Tr(
            Td(full_name, cls="graph-sidebar__td"),
            Td(item.get("kind", "\u2014"), cls="graph-sidebar__td"),
            Td(", ".join(noc) or "\u2014", cls="graph-sidebar__td"),
            Td(item.get("notified_on", "\u2014"), cls="graph-sidebar__td"),
            Td(badge, cls="graph-sidebar__td"),
        )

    return Div(Table(
        Thead(Tr(
            Th("Name", cls="graph-sidebar__th"), Th("Kind", cls="graph-sidebar__th"),
            Th("Natures of Control", cls="graph-sidebar__th"),
            Th("Notified", cls="graph-sidebar__th"), Th("Status", cls="graph-sidebar__th"),
        )),
        Tbody(*[_row(i) for i in items]),
        cls="graph-sidebar__table enrich-table",
    ))


def _company_tab_filings(items: list) -> FT:
    if not items:
        return P("No filings found.", cls="enrich-empty")

    def _row(item: dict) -> FT:
        doc_link = item.get("links", {}).get("document_metadata", "")
        doc_cell = A("View \u2197", href=doc_link, target="_blank", cls="enrich-ch-link") if doc_link else Span("\u2014")
        return Tr(
            Td(item.get("type", "\u2014"), cls="graph-sidebar__td"),
            Td(item.get("description", item.get("type", "\u2014")), cls="graph-sidebar__td"),
            Td(item.get("date", "\u2014"), cls="graph-sidebar__td"),
            Td(doc_cell, cls="graph-sidebar__td"),
        )

    return Div(Table(
        Thead(Tr(
            Th("Type", cls="graph-sidebar__th"), Th("Description", cls="graph-sidebar__th"),
            Th("Date", cls="graph-sidebar__th"), Th("Doc", cls="graph-sidebar__th"),
        )),
        Tbody(*[_row(i) for i in items]),
        cls="graph-sidebar__table enrich-table",
    ))


def _company_tab_charges(items: list) -> FT:
    if not items:
        return P("No charges found.", cls="enrich-empty")

    def _row(item: dict) -> FT:
        entitled = item.get("persons_entitled") or []
        entitled_str = ", ".join(
            p.get("name", "") for p in entitled if isinstance(p, dict)
        ) if entitled else "\u2014"
        return Tr(
            Td(item.get("charge_code", "\u2014"), cls="graph-sidebar__td"),
            Td(item.get("status", "\u2014"), cls="graph-sidebar__td"),
            Td(entitled_str, cls="graph-sidebar__td"),
            Td(item.get("created_on", "\u2014"), cls="graph-sidebar__td"),
            Td(item.get("satisfied_on", "\u2014"), cls="graph-sidebar__td"),
        )

    return Div(Table(
        Thead(Tr(
            Th("Code", cls="graph-sidebar__th"), Th("Status", cls="graph-sidebar__th"),
            Th("Entitled", cls="graph-sidebar__th"), Th("Created", cls="graph-sidebar__th"),
            Th("Satisfied", cls="graph-sidebar__th"),
        )),
        Tbody(*[_row(i) for i in items]),
        cls="graph-sidebar__table enrich-table",
    ))


def _company_tab_more(company_number: str, result: dict) -> FT:
    payloads = result.get("payloads", {})
    endpoints_called = result.get("endpoints_called", [])
    endpoints_skipped = result.get("endpoints_skipped", [])

    insolvency_items = payloads.get("insolvency", {}).get("cases", [])

    def _insolvency_row(case: dict) -> FT:
        practitioners = case.get("practitioners") or []
        prac_str = ", ".join(p.get("name", "") for p in practitioners if isinstance(p, dict)) or "\u2014"
        dates = case.get("dates") or []
        date_str = ", ".join(f"{d.get('type','')}: {d.get('date','')}" for d in dates if isinstance(d, dict)) or "\u2014"
        return Tr(
            Td(case.get("type", "\u2014"), cls="graph-sidebar__td"),
            Td(str(case.get("number", "\u2014")), cls="graph-sidebar__td"),
            Td(prac_str, cls="graph-sidebar__td"),
            Td(date_str, cls="graph-sidebar__td"),
        )

    insolvency_section = Div()
    if insolvency_items:
        insolvency_section = Div(
            P("Insolvency", cls="enrich-more__section-title"),
            Table(
                Thead(Tr(
                    Th("Type", cls="graph-sidebar__th"), Th("Number", cls="graph-sidebar__th"),
                    Th("Practitioners", cls="graph-sidebar__th"), Th("Dates", cls="graph-sidebar__th"),
                )),
                Tbody(*[_insolvency_row(c) for c in insolvency_items]),
                cls="graph-sidebar__table enrich-table",
            ),
        )

    download_endpoints = [
        ("registers", "Registers"),
        ("exemptions", "Exemptions"),
        ("uk-establishments", "UK Establishments"),
    ]
    downloads = []
    for ep_key, ep_label in download_endpoints:
        if ep_key in endpoints_called:
            downloads.append(A(
                f"\u2b07 {ep_label} JSON",
                href=f"/companies-graph/download/{company_number}/{ep_key}",
                cls="enrich-download-btn",
                download=True,
            ))
        elif ep_key in endpoints_skipped:
            downloads.append(Span(f"{ep_label} (skipped \u2014 rate limit)", cls="enrich-skipped"))

    return Div(
        insolvency_section,
        Div(*downloads, cls="enrich-more__downloads") if downloads else Div(),
    )


# ---------------------------------------------------------------------------
# Officer enrichment panel (Sprint 4)
# ---------------------------------------------------------------------------

def officer_enrichment_panel(result: dict, officer_id: str) -> FT:
    payloads = result.get("payloads", {})
    graph_elements = result.get("graph_elements", [])

    appointments_data = payloads.get("appointments", {})
    disq_natural = payloads.get("disqualified-natural", {})
    disq_corporate = payloads.get("disqualified-corporate", {})
    disq_data = disq_natural if disq_natural.get("disqualifications") else disq_corporate

    tabs = [
        ("overview",          "Overview",          _officer_tab_overview(appointments_data, disq_data)),
        ("appointments",      "Appointments",      _officer_tab_appointments(appointments_data.get("items", []), officer_id)),
        ("disqualifications", "Disqualifications", _officer_tab_disqualifications(disq_data)),
    ]

    merge_script = Script(
        f"if(typeof mergeElements==='function'){{mergeElements({json.dumps(graph_elements)});setEnrichedNode('p_{officer_id}')}}",
        type="text/javascript",
    ) if graph_elements else Script(
        f"setEnrichedNode('p_{officer_id}')",
        type="text/javascript",
    )

    return _tab_panel(tabs, merge_script)


def _officer_tab_overview(appointments_data: dict, disq_data: dict) -> FT:
    items = appointments_data.get("items", [])
    total = appointments_data.get("total_results", len(items))
    active_items = [i for i in items if not i.get("resigned_on")]
    nationality = country = dob_str = ""
    if items:
        first = items[0]
        nationality = first.get("nationality", "")
        country = first.get("country_of_residence", "")
        dob = first.get("date_of_birth") or {}
        if dob.get("year"):
            dob_str = str(dob["year"]) + (f"-{dob['month']:02d}" if dob.get("month") else "")

    disq_list = disq_data.get("disqualifications", [])
    if disq_list:
        until_dates = [d.get("disqualified_until", "") for d in disq_list if d.get("disqualified_until")]
        disq_status = Span(
            f"Disqualified until {max(until_dates)}" if until_dates else "Disqualified",
            cls="enrich-badge enrich-badge--resigned",
        )
    else:
        disq_status = Span("Not disqualified", cls="enrich-badge enrich-badge--active")

    fields = [
        ("Nationality",          nationality),
        ("Country of Residence", country),
        ("Date of Birth",        dob_str),
        ("Total Appointments",   str(total) if total else None),
        ("Active Appointments",  str(len(active_items)) if active_items else None),
    ]
    rows = [
        Tr(Th(k, cls="graph-sidebar__th"), Td(v or "\u2014", cls="graph-sidebar__td"))
        for k, v in fields if v
    ]
    return Div(
        Table(*rows, cls="graph-sidebar__table") if rows else Div(),
        Div(Span("Disqualification status: ", cls="enrich-label"), disq_status, cls="enrich-disq-status"),
    )


def _officer_tab_appointments(items: list, officer_id: str) -> FT:
    if not items:
        return P("No appointments found.", cls="enrich-empty")

    active = [i for i in items if not i.get("resigned_on")]
    resigned = [i for i in items if i.get("resigned_on")]

    def _row(item: dict) -> FT:
        apt = item.get("appointed_to") or {}
        co_number = apt.get("company_number", "")
        co_name = apt.get("company_name", co_number or "\u2014")
        co_status = apt.get("company_status", "")
        is_active = not bool(item.get("resigned_on"))
        name_cell = (
            Button(co_name, cls="enrich-officer-link",
                   onclick=f"fetchDetail('Company', '{co_number}')")
            if co_number else Span(co_name)
        )
        badge = Span("Active", cls="enrich-badge enrich-badge--active") if is_active else Span("Resigned", cls="enrich-badge enrich-badge--resigned")
        return Tr(
            Td(name_cell, cls="graph-sidebar__td"),
            Td(item.get("officer_role", "\u2014"), cls="graph-sidebar__td"),
            Td(str(item.get("appointed_on") or "\u2014"), cls="graph-sidebar__td"),
            Td(str(item.get("resigned_on") or "\u2014"), cls="graph-sidebar__td"),
            Td(co_status or "\u2014", cls="graph-sidebar__td"),
            Td(badge, cls="graph-sidebar__td"),
        )

    active_co_numbers = [
        (i.get("appointed_to") or {}).get("company_number", "")
        for i in active if (i.get("appointed_to") or {}).get("company_number")
    ]
    add_all_btn = Button(
        f"Add {len(active_co_numbers)} active companies to graph",
        cls="graph-sidebar__enrich-btn enrich-add-all-btn",
        onclick=f"addOfficerCompaniesToGraph({json.dumps(active_co_numbers)})",
    ) if active_co_numbers else Div()

    return Div(
        add_all_btn,
        Table(
            Thead(Tr(
                Th("Company", cls="graph-sidebar__th"), Th("Role", cls="graph-sidebar__th"),
                Th("Appointed", cls="graph-sidebar__th"), Th("Resigned", cls="graph-sidebar__th"),
                Th("Co. Status", cls="graph-sidebar__th"), Th("Status", cls="graph-sidebar__th"),
            )),
            Tbody(*[_row(i) for i in active + resigned]),
            cls="graph-sidebar__table enrich-table",
        ),
    )


def _officer_tab_disqualifications(disq_data: dict) -> FT:
    disq_list = disq_data.get("disqualifications", [])
    if not disq_list:
        return P("No disqualification record found.", cls="enrich-empty")

    def _row(d: dict) -> FT:
        case_ids = d.get("case_identifier", {})
        case_num = case_ids.get("number", "") if isinstance(case_ids, dict) else str(case_ids)
        co_names = [co for co in (d.get("company_names") or []) if isinstance(co, str)]
        return Tr(
            Td(str(d.get("disqualification_type", "\u2014")), cls="graph-sidebar__td"),
            Td(str(d.get("disqualified_from") or "\u2014"), cls="graph-sidebar__td"),
            Td(str(d.get("disqualified_until") or "Indefinite"), cls="graph-sidebar__td"),
            Td(case_num or "\u2014", cls="graph-sidebar__td"),
            Td(", ".join(co_names) or "\u2014", cls="graph-sidebar__td"),
        )

    return Div(Table(
        Thead(Tr(
            Th("Type", cls="graph-sidebar__th"), Th("From", cls="graph-sidebar__th"),
            Th("Until", cls="graph-sidebar__th"), Th("Case No.", cls="graph-sidebar__th"),
            Th("Companies", cls="graph-sidebar__th"),
        )),
        Tbody(*[_row(d) for d in disq_list]),
        cls="graph-sidebar__table enrich-table",
    ))
