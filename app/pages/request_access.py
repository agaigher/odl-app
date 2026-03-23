from fasthtml.common import *
from app.supabase_db import db_select


def RequestAccessPage(slug: str, access_type: str, session=None):
    try:
        rows = db_select("datasets", {"slug": slug})
        dataset = rows[0] if rows else None
    except Exception:
        dataset = None

    title = dataset.get("title") if dataset else slug
    is_snowflake = access_type == "snowflake"

    return Html(
        Head(
            Title(f"{'Add to Snowflake' if is_snowflake else 'Get API Access'} | OpenData.London"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            Style("""
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { background: #0B1120; font-family: 'Inter', sans-serif; min-height: 100vh; display: flex; flex-direction: column; }
                .auth-topbar { display: flex; align-items: center; justify-content: space-between; padding: 18px 40px; border-bottom: 1px solid rgba(255,255,255,0.06); }
                .auth-brand { font-size: 17px; font-weight: 700; color: #fff; text-decoration: none; }
                .auth-brand span { color: #0284C7; }
                .auth-wrapper { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }
                .auth-card { width: 100%; max-width: 480px; }
                .ds-pill { display: inline-flex; align-items: center; gap: 8px; background: rgba(2,132,199,0.08); border: 1px solid rgba(2,132,199,0.2); color: #0284C7; padding: 5px 12px; border-radius: 6px; font-size: 13px; font-weight: 500; margin-bottom: 20px; }
                .auth-heading { font-size: 24px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.4px; margin-bottom: 6px; }
                .auth-subheading { font-size: 14px; color: #64748B; margin-bottom: 28px; line-height: 1.6; }
                .info-box { background: #0F1929; border: 1px solid rgba(148,163,184,0.12); border-radius: 8px; padding: 16px 18px; margin-bottom: 22px; font-size: 13px; color: #94A3B8; line-height: 1.6; }
                .info-box strong { color: #CBD5E1; }
                .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
                .form-label { font-size: 13px; font-weight: 500; color: #CBD5E1; }
                .form-hint { font-size: 12px; color: #475569; margin-top: 3px; }
                .form-input { width: 100%; background: #020617; border: 1px solid rgba(148,163,184,0.18); color: #F8FAFC; padding: 11px 14px; border-radius: 7px; font-family: 'Inter', sans-serif; font-size: 14px; transition: border-color 0.2s; }
                .form-input:focus { outline: none; border-color: #0284C7; }
                .form-input::placeholder { color: #334155; }
                .auth-submit-btn { width: 100%; background: #0284C7; color: #020617; font-weight: 700; font-size: 14px; padding: 12px; border: none; border-radius: 7px; cursor: pointer; font-family: 'Inter', sans-serif; transition: opacity 0.2s; margin-top: 8px; }
                .auth-submit-btn:hover { opacity: 0.88; }
                .auth-message { min-height: 20px; text-align: center; font-size: 13px; margin-top: 14px; line-height: 1.5; }
                .error-text { color: #EF4444; }
                .success-text { color: #10B981; }
                .auth-card-footer { text-align: center; font-size: 13px; color: #475569; margin-top: 22px; }
                .auth-card-footer a { color: #0284C7; font-weight: 500; text-decoration: none; }
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
                    Div(
                        NotStr('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>'),
                        title,
                        cls="ds-pill"
                    ),
                    H1(
                        "Add to your Snowflake account" if is_snowflake else "Activate API access",
                        cls="auth-heading"
                    ),
                    P(
                        "We'll create a zero-copy Snowflake listing so you can query the data directly from your warehouse — no data movement, no duplication." if is_snowflake
                        else "Activating API access lets you query this dataset using your API key. You'll be redirected to your keys page once confirmed.",
                        cls="auth-subheading"
                    ),
                    *(
                        [Div(
                            P(NotStr("<strong>How it works:</strong> Once submitted, we'll provision a Snowflake Data Share from our account to yours within 24 hours. You'll receive an email when it's ready, with instructions to accept the listing in your Snowflake account.")),
                            cls="info-box"
                        )]
                        if is_snowflake else []
                    ),
                    Form(
                        Input(type="hidden", name="access_type", value=access_type),
                        *(
                            [Div(
                                Label("Your Snowflake account identifier", fr="snowflake_account", cls="form-label"),
                                Input(type="text", id="snowflake_account", name="snowflake_account",
                                      placeholder="e.g. KQAUKRN-JG40879", cls="form-input",
                                      value=session.get('sf_account', '') if session else ''),
                                P("Found in Snowflake → bottom-left corner → hover your account name", cls="form-hint"),
                                cls="form-group"
                            )]
                            if is_snowflake else []
                        ),
                        Button(
                            "Request Snowflake Share" if is_snowflake else "Activate API Access",
                            type="submit", cls="auth-submit-btn"
                        ),
                        hx_post=f"/catalog/{slug}/request-access",
                        hx_target="#access-message"
                    ),
                    Div(id="access-message", cls="auth-message"),
                    Div(A(f"← Back to {title}", href=f"/catalog/{slug}"), cls="auth-card-footer"),
                    cls="auth-card"
                ),
                cls="auth-wrapper"
            )
        )
    )
