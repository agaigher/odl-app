"""
Billing routes: billing page, checkout, spend-cap, emails, address.
"""
from fasthtml.common import *
import stripe

from app.config import STRIPE_API_KEY
from app.auth.middleware import get_user_id
from app.db import db_select, db_patch, log_audit
from app.ui.components import page_layout

stripe.api_key = STRIPE_API_KEY


def register(rt):

    @rt("/billing")
    def get_billing(session):
        from app.pages.billing import BillingDashboard
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        return page_layout("Billing", "/billing", session.get('user'),
                           BillingDashboard(user_id=user_id, session=session))

    @rt("/billing/checkout", methods=["POST"])
    def post_billing_checkout(req, session, package: str):
        user_id = get_user_id(session)
        if not user_id:
            return RedirectResponse("/login", status_code=303)
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            org_id = memberships[0]["org_id"] if memberships else None
            billing_email = None
            if org_id:
                org_rows = db_select("organisations", {"id": org_id})
                if org_rows:
                    billing_email = org_rows[0].get("billing_email")
        except Exception:
            org_id = None
        if not org_id:
            return Div("Organization not found", cls="error-text")
        domain = str(req.base_url).rstrip("/")
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'gbp',
                        'product_data': {
                            'name': '10,000 Data Credits',
                            'description': 'Prepaid compute and API querying credits for OpenData.London',
                        },
                        'unit_amount': 1000,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                metadata={'org_id': org_id, 'credits_to_add': 10000},
                customer_email=billing_email if billing_email else None,
                success_url=f"{domain}/billing?success=true",
                cancel_url=f"{domain}/billing?canceled=true",
            )
            return RedirectResponse(checkout_session.url, status_code=303)
        except Exception as e:
            return Div(f"Error creating checkout: {e}", cls="error-text")

    @rt("/billing/spend-cap", methods=["POST"])
    def post_billing_spend_cap(session, enabled: bool = False):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            db_patch("organisations", {"spend_cap_enabled": enabled}, {"id": org_id})
            log_audit(org_id, user_id, f"{'Enabled' if enabled else 'Disabled'} billing spend cap", "billing", org_id)
            return ""
        except Exception:
            return "Error", 500

    @rt("/billing/emails", methods=["POST"])
    def post_billing_emails(session, billing_email: str, additional_emails: str = ""):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            db_patch("organisations", {
                "billing_email": billing_email,
                "additional_billing_emails": additional_emails,
            }, {"id": org_id})
            log_audit(org_id, user_id, "Updated billing recipients", "billing", org_id)
            return Div("Billing emails updated.", cls="success-text", style="margin-top: 8px;")
        except Exception as e:
            return f"Error: {e}", 500

    @rt("/billing/address", methods=["POST"])
    def post_billing_address(session, billing_name: str, billing_address_line1: str,
                             billing_address_line2: str = "", billing_country: str = "",
                             billing_postal_code: str = "", billing_city: str = "",
                             billing_state: str = "", billing_tax_id_type: str = "",
                             tax_id: str = ""):
        user_id = get_user_id(session)
        if not user_id:
            return "Unauthorized", 401
        try:
            memberships = db_select("memberships", {"user_id": user_id, "status": "active"})
            if not memberships:
                return "No active organization", 400
            org_id = memberships[0]["org_id"]
            db_patch("organisations", {
                "billing_name": billing_name,
                "billing_address_line1": billing_address_line1,
                "billing_address_line2": billing_address_line2,
                "billing_country": billing_country,
                "billing_postal_code": billing_postal_code,
                "billing_city": billing_city,
                "billing_state": billing_state,
                "billing_tax_id_type": billing_tax_id_type,
                "tax_id": tax_id,
            }, {"id": org_id})
            log_audit(org_id, user_id, "Updated billing address and tax info", "billing", org_id)
            return Div("Billing address updated.", cls="success-text", style="margin-top: 8px;")
        except Exception as e:
            return f"Error: {e}", 500
