"""
Invite acceptance routes: /invite/accept, /invite/confirm, /org/{slug}/invite.
"""
from fasthtml.common import *
from app.config import APP_URL
from app.auth.client import get_auth_client
from app.db import db_select, db_insert, db_patch, auth_invite, log_audit
from app.email import send_org_invite
from app.pages.invite import InvitePage
from app.ui.styles import get_critical_canvas_style, get_focus_ring_reset_style


def register(rt):

    @rt("/org/{slug}/invite", methods=["GET"])
    def get_invite(slug: str, session):
        orgs = db_select("organisations", {"slug": slug})
        if not orgs:
            return RedirectResponse(f"/org/{slug}", status_code=303)
        return InvitePage(slug=slug, org_name=orgs[0]["name"])

    @rt("/org/{slug}/invite", methods=["POST"])
    def post_invite(slug: str, invited_email: str, role: str, session):
        if not session.get('user'):
            return Div("Not authenticated.", cls="error-text")
        if not invited_email:
            return Div("Email is required.", cls="error-text")
        if role not in ("admin", "member"):
            role = "member"
        try:
            orgs = db_select("organisations", {"slug": slug})
            if not orgs:
                return Div("Organisation not found.", cls="error-text")
            org_id = orgs[0]["id"]
            org_name = orgs[0]["name"]
            db_insert("memberships", {
                "org_id": org_id, "invited_email": invited_email,
                "role": role, "status": "pending",
            })
            result = auth_invite(email=invited_email, redirect_to=f"{APP_URL}/invite/accept?org={slug}")
            invite_link = result.get("action_link", "")
            email_sent = send_org_invite(
                invited_email=invited_email, org_name=org_name, role=role,
                invite_link=invite_link, invited_by=session.get('user', ''),
            )
            if email_sent:
                return Div(f"Invitation sent to {invited_email}.", cls="success-text")
            return Div(
                P(f"Membership record created for {invited_email}.",
                  style="color: #10B981; font-size: 13px; margin-bottom: 10px;"),
                P("Email delivery is not configured. Share this link manually:",
                  style="color: #94A3B8; font-size: 13px; margin-bottom: 8px;"),
                Input(type="text", value=invite_link, readonly=True,
                      style="width: 100%; background: #0F1929; border: 1px solid rgba(148,163,184,0.2); "
                            "color: #CBD5E1; padding: 8px 12px; border-radius: 6px; font-size: 12px; font-family: monospace;"),
            )
        except Exception as e:
            err = str(e)
            if "duplicate key" in err or "unique" in err.lower():
                return Div("That person is already a member or has a pending invite.", cls="error-text")
            return Div(f"Error: {err}", cls="error-text")

    @rt("/invite/accept")
    def get_invite_accept(req, session, org: str = ""):
        return Html(
            Head(
                Title("Accepting Invitation | OpenData.London"),
                get_critical_canvas_style(bg="#080a0f", fg="#f8fafc"),
                Meta(name="theme-color", content="#080a0f"),
                Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
                Style("""
                    * { box-sizing: border-box; margin: 0; padding: 0; }
                    body { background: #080a0f; font-family: 'Inter', sans-serif; min-height: 100vh;
                           display: flex; align-items: center; justify-content: center; color: #F8FAFC; }
                    .card { text-align: center; max-width: 400px; padding: 40px 20px; }
                    .card h1 { font-size: 22px; font-weight: 700; margin-bottom: 10px; }
                    .card p { color: #64748B; font-size: 14px; line-height: 1.6; }
                """),
                get_focus_ring_reset_style(),
            ),
            Body(
                Div(
                    H1("Joining your organisation\u2026"),
                    P("Please wait while we set up your access."),
                    cls="card"
                ),
                Script(f"""
                    const hash = window.location.hash.substring(1);
                    const params = new URLSearchParams(hash);
                    const token = params.get('access_token');
                    const org = "{org}";
                    if (token) {{
                        fetch('/invite/confirm', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{access_token: token, org: org}})
                        }}).then(r => r.json()).then(d => {{
                            if (d.ok) window.location.href = '/org/' + org;
                            else document.querySelector('p').textContent = 'Error: ' + d.error;
                        }});
                    }} else {{
                        document.querySelector('p').textContent = 'Invalid or expired invite link.';
                    }}
                """)
            )
        )

    @rt("/invite/confirm", methods=["POST"])
    async def post_invite_confirm(req, session):
        try:
            body = await req.json()
            access_token = body.get("access_token", "")
            org_slug = body.get("org", "")
            supabase = get_auth_client()
            user = supabase.get_user(access_token)
            user_email = user.user.email
            user_id = str(user.user.id)
            session['user'] = user_email
            session['access_token'] = access_token
            orgs = db_select("organisations", {"slug": org_slug})
            if orgs:
                org_id = orgs[0]["id"]
                db_patch("memberships",
                         data={"user_id": user_id, "status": "active"},
                         filters={"org_id": org_id, "invited_email": user_email})
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
