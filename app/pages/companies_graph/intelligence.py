"""
Sprint 5 — Intelligence Layer sidebar components.

These are HTMX partial responses loaded lazily when a node is tapped:
  GET /companies-graph/intelligence/company/{number}  → company_health_panel()
  GET /companies-graph/intelligence/person/{id}       → person_intelligence_panel()
"""
from __future__ import annotations

from fasthtml.common import (
    A, Button, Div, Li, P, Script, Span,
    Table, Tbody, Td, Th, Thead, Tr, Ul, FT,
)


# ---------------------------------------------------------------------------
# Company intelligence
# ---------------------------------------------------------------------------

def company_health_panel(health: dict, co_location: list, company_number: str) -> FT:
    """
    Inline intelligence panel for a Company node.
    Shows health flags, co-located companies count.
    Loaded via HTMX on node tap.
    """
    flags = health.get("health_flags", [])
    last_filing = health.get("last_filing_date", "")
    outstanding_charges = health.get("outstanding_charges", 0)
    active_insolvency = health.get("active_insolvency", False)
    active_officers = health.get("active_officers", 0)
    total_officers = health.get("total_officers", 0)
    all_resigned = health.get("all_officers_resigned", False)
    is_shell = health.get("shell_company", False)

    flag_items = []

    if is_shell:
        flag_items.append(Div(
            Span("\u26a0", cls="intel-flag__icon intel-flag__icon--high"),
            Span("Shell company indicators present", cls="intel-flag__text"),
            cls="intel-flag intel-flag--high",
        ))

    if "filing_overdue" in flags:
        label = f"Filing overdue (last: {last_filing})" if last_filing else "Filing overdue"
        flag_items.append(Div(
            Span("\u26a0", cls="intel-flag__icon intel-flag__icon--medium"),
            Span(label, cls="intel-flag__text"),
            cls="intel-flag intel-flag--medium",
        ))

    if outstanding_charges:
        flag_items.append(Div(
            Span("\u26a0", cls="intel-flag__icon intel-flag__icon--medium"),
            Span(f"{outstanding_charges} outstanding charge{'s' if outstanding_charges != 1 else ''}", cls="intel-flag__text"),
            cls="intel-flag intel-flag--medium",
        ))

    if active_insolvency:
        flag_items.append(Div(
            Span("\u26a0", cls="intel-flag__icon intel-flag__icon--high"),
            Span("Active insolvency case", cls="intel-flag__text"),
            cls="intel-flag intel-flag--high",
        ))

    if not flags and not is_shell:
        flag_items.append(Div(
            Span("\u2713", cls="intel-flag__icon intel-flag__icon--ok"),
            Span("No health flags", cls="intel-flag__text"),
            cls="intel-flag intel-flag--ok",
        ))

    officer_text = f"{active_officers} of {total_officers} officer{'s' if total_officers != 1 else ''} active"
    if all_resigned:
        officer_text = "All officers resigned"

    co_loc_section = Div()
    if co_location:
        co_loc_section = Div(
            Span(
                f"{len(co_location)} other {'company' if len(co_location) == 1 else 'companies'} at this address",
                cls="intel-colocation__label",
            ),
            Button(
                "Load all onto graph",
                cls="intel-colocation__btn",
                onclick=f"addColocatedToGraph({[c['company_number'] for c in co_location]!r})",
            ),
            cls="intel-colocation",
        )

    return Div(
        Div(
            Span("Health", cls="intel-section__title"),
            *flag_items,
            Div(
                Span("\u2022", cls="intel-flag__icon"),
                Span(officer_text, cls="intel-flag__text"),
                cls="intel-flag",
            ),
            cls="intel-section",
        ),
        co_loc_section,
        cls="intel-panel",
    )


# ---------------------------------------------------------------------------
# Person intelligence
# ---------------------------------------------------------------------------

def person_intelligence_panel(
    risk: dict,
    tenure: dict,
    cyto_node_id: str,
) -> FT:
    """
    Inline intelligence panel for a Person node.
    Shows risk level badge, signal summary, tenure stats.
    Also emits a <script> to apply risk_level to the Cytoscape node.
    """
    risk_level = risk.get("risk_level", "low")
    signals = risk.get("signals", [])

    # Risk badge
    badge_cls = {
        "high":   "intel-risk-badge--high",
        "medium": "intel-risk-badge--medium",
        "low":    "intel-risk-badge--low",
    }.get(risk_level, "intel-risk-badge--low")

    badge_label = {
        "high":   "\u26a0 High Risk",
        "medium": "\u26a0 Medium Risk",
        "low":    "\u2713 Low Risk",
    }.get(risk_level, "\u2713 Low Risk")

    signal_items = [
        Div(Span(s, cls="intel-signal__text"), cls="intel-signal")
        for s in signals
    ] if signals else [Div(Span("No risk signals detected", cls="intel-signal__text"), cls="intel-signal")]

    # Tenure stats
    tenure_parts = []
    if tenure:
        avg_days = tenure.get("avg_tenure_days")
        short_count = tenure.get("short_tenure_count", 0)
        dissolved_count = tenure.get("dissolved_while_director", 0)
        if avg_days is not None:
            avg_months = round(avg_days / 30)
            tenure_parts.append(f"Avg tenure: {avg_months}mo")
        if short_count:
            tenure_parts.append(f"{short_count} short (<6mo)")
        if dissolved_count:
            tenure_parts.append(f"{dissolved_count} dissolved while director")

    tenure_section = Div()
    if tenure_parts:
        tenure_section = Div(
            Span("Tenure: " + " · ".join(tenure_parts), cls="intel-tenure__summary"),
            cls="intel-tenure",
        )

    # Emit script to apply risk_level colour to the canvas node
    risk_script = Script(
        f"if(typeof applyRiskLevel==='function'){{applyRiskLevel('{cyto_node_id}', '{risk_level}')}}",
        type="text/javascript",
    )

    return Div(
        Div(
            Span(badge_label, cls=f"intel-risk-badge {badge_cls}"),
            *signal_items,
            cls="intel-section",
        ),
        tenure_section,
        risk_script,
        cls="intel-panel",
    )


def person_intelligence_error() -> FT:
    return Div(cls="intel-panel")  # silent fail — don't break sidebar


# ---------------------------------------------------------------------------
# Ownership chain (Sprint 5d)
# ---------------------------------------------------------------------------

def ownership_chain_panel(chain: list[dict]) -> FT:
    """
    Sidebar section showing the PSC_CORPORATE ownership chain above this company.
    Each hop is a row with company name, jurisdiction, control type, and an
    "Add to graph" button. Ceased PSCs are rendered greyed out.
    """
    if not chain:
        return Div(
            Span("Ownership chain", cls="intel-section__title"),
            Div(
                Span("✓", cls="intel-flag__icon intel-flag__icon--ok"),
                Span("No corporate PSC owners found", cls="intel-flag__text"),
                cls="intel-flag intel-flag--ok",
            ),
            cls="intel-section",
        )

    rows = []
    current_depth = None
    for hop in chain:
        depth = hop["depth"]
        is_active = hop["is_active"]
        is_offshore = hop["is_offshore"]
        name = hop["name"]
        number = hop["company_number"]
        jurisdiction = hop["jurisdiction"]
        ceased_on = hop["ceased_on"]
        notified_on = hop["notified_on"]
        noc = hop.get("natures_of_control") or []

        # Depth label when level changes
        if depth != current_depth:
            current_depth = depth
            level_label = "Immediate owner" if depth == 1 else f"Level {depth} owner"
            rows.append(Div(level_label, cls="ownership-chain__level-label"))

        # Badges
        badges = []
        if is_offshore:
            badges.append(Span("Offshore", cls="ownership-chain__badge ownership-chain__badge--offshore"))
        if not is_active:
            badges.append(Span(f"Ceased {ceased_on}" if ceased_on else "Ceased", cls="ownership-chain__badge ownership-chain__badge--ceased"))

        # Nature of control — shorten common verbose strings
        noc_display = []
        for n in noc:
            short = (n
                     .replace("ownership-of-shares-", "")
                     .replace("voting-rights-", "")
                     .replace("-percent-", "% ")
                     .replace("-as-trust", " (trust)")
                     .replace("-as-firm", " (firm)")
                     .replace("-limited-liability-partnership", "")
                     .replace("-", " ")
                     .strip())
            noc_display.append(short)
        noc_text = " · ".join(noc_display) if noc_display else ""

        meta_parts = []
        if jurisdiction:
            meta_parts.append(jurisdiction)
        if notified_on:
            meta_parts.append(f"from {notified_on}")

        row_cls = "ownership-chain__row" + (" ownership-chain__row--ceased" if not is_active else "")
        rows.append(Div(
            Div(
                Div(
                    Span(name, cls="ownership-chain__name"),
                    *badges,
                    cls="ownership-chain__name-row",
                ),
                Div(
                    Span(" · ".join(meta_parts), cls="ownership-chain__meta") if meta_parts else Span(),
                    Span(noc_text, cls="ownership-chain__noc") if noc_text else Span(),
                    cls="ownership-chain__detail",
                ),
                cls="ownership-chain__info",
            ),
            Button(
                "+ Graph",
                cls="ownership-chain__add-btn",
                onclick=f"addOwnerToGraph({number!r}, {name!r})",
                title=f"Add {name} to graph",
            ),
            cls=row_cls,
        ))

    return Div(
        Span("Ownership chain", cls="intel-section__title"),
        *rows,
        cls="intel-section",
    )
