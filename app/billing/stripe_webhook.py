"""
Stripe webhook handler — isolated for security review.
"""
import stripe
from app.config import STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET
from app.db import db_insert, db_select, db_patch

stripe.api_key = STRIPE_API_KEY


def register(rt):

    @rt("/api/webhooks/stripe", methods=["POST"])
    async def stripe_webhook(req):
        payload = await req.body()
        sig_header = req.headers.get("stripe-signature")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except ValueError:
            return "Invalid payload", 400
        except stripe.error.SignatureVerificationError:
            return "Invalid signature", 400

        if event['type'] == 'checkout.session.completed':
            session_data = event['data']['object']
            org_id = session_data.get('metadata', {}).get('org_id')
            credits_str = session_data.get('metadata', {}).get('credits_to_add')
            session_id = session_data.get('id')

            if org_id and credits_str:
                try:
                    db_insert("billing_ledger", {
                        "org_id": org_id,
                        "stripe_session_id": session_id,
                        "amount_paid": session_data.get('amount_total', 0) / 100.0,
                        "credits_added": int(credits_str),
                        "status": "completed",
                    })
                    orgs = db_select("organisations", {"id": org_id})
                    if orgs:
                        current_balance = orgs[0].get("credit_balance", 0)
                        new_balance = current_balance + int(credits_str)
                        db_patch("organisations", {"credit_balance": new_balance}, {"id": org_id})
                except Exception as e:
                    print("Webhook processing error:", e)

        return "Success", 200
