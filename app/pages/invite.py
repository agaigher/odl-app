from fasthtml.common import *


def InvitePage(slug: str, org_name: str):
    return Html(
        Head(
            Title(f"Invite Member | {org_name}"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            Style("""
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { background: #0B1120; font-family: 'Inter', sans-serif; min-height: 100vh; display: flex; flex-direction: column; }
                .auth-topbar { display: flex; align-items: center; justify-content: space-between; padding: 18px 40px; border-bottom: 1px solid rgba(255,255,255,0.06); }
                .auth-brand { font-size: 17px; font-weight: 700; color: #fff; text-decoration: none; }
                .auth-brand span { color: #29b5e8; }
                .auth-wrapper { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }
                .auth-card { width: 100%; max-width: 460px; }
                .auth-heading { font-size: 26px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.5px; margin-bottom: 6px; }
                .auth-subheading { font-size: 14px; color: #64748B; margin-bottom: 32px; line-height: 1.6; }
                .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
                .form-label { font-size: 13px; font-weight: 500; color: #CBD5E1; }
                .form-input { width: 100%; background: #020617; border: 1px solid rgba(148,163,184,0.18); color: #F8FAFC; padding: 11px 14px; border-radius: 7px; font-family: 'Inter', sans-serif; font-size: 14px; transition: border-color 0.2s; }
                .form-input:focus { outline: none; border-color: #29b5e8; }
                .form-input::placeholder { color: #334155; }
                select.form-input { cursor: pointer; }
                .auth-submit-btn { width: 100%; background: #29b5e8; color: #020617; font-weight: 700; font-size: 14px; padding: 12px; border: none; border-radius: 7px; cursor: pointer; font-family: 'Inter', sans-serif; transition: opacity 0.2s; margin-top: 8px; }
                .auth-submit-btn:hover { opacity: 0.88; }
                .auth-message { min-height: 20px; text-align: center; font-size: 13px; margin-top: 12px; }
                .error-text { color: #EF4444; }
                .success-text { color: #10B981; }
                .auth-card-footer { text-align: center; font-size: 13px; color: #475569; margin-top: 24px; }
                .auth-card-footer a { color: #29b5e8; font-weight: 500; text-decoration: none; }
                .auth-card-footer a:hover { text-decoration: underline; }
            """)
        ),
        Body(
            Div(
                A("OpenData", Span(".London"), href="https://www.opendata.london", cls="auth-brand"),
                cls="auth-topbar"
            ),
            Div(
                Div(
                    H1("Invite a team member", cls="auth-heading"),
                    P(f"They'll receive an email invitation to join {org_name}.", cls="auth-subheading"),
                    Form(
                        Input(type="hidden", name="slug", value=slug),
                        Div(
                            Label("Email address", fr="invited_email", cls="form-label"),
                            Input(type="email", id="invited_email", name="invited_email", required=True,
                                  placeholder="colleague@company.com", cls="form-input"),
                            cls="form-group"
                        ),
                        Div(
                            Label("Role", fr="role", cls="form-label"),
                            Select(
                                Option("Member — can view data and use API keys", value="member", selected=True),
                                Option("Admin — can manage members and settings", value="admin"),
                                id="role", name="role", cls="form-input"
                            ),
                            cls="form-group"
                        ),
                        Button("Send Invitation", type="submit", cls="auth-submit-btn"),
                        hx_post=f"/org/{slug}/invite",
                        hx_target="#invite-message"
                    ),
                    Div(id="invite-message", cls="auth-message"),
                    Div(A(f"← Back to {org_name}", href=f"/org/{slug}"), cls="auth-card-footer"),
                    cls="auth-card"
                ),
                cls="auth-wrapper"
            )
        )
    )
