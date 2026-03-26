from fasthtml.common import *

from app.auth.password_policy import PASSWORD_POLICY_HINT, password_policy_html_pattern


def ForgotPasswordPage():
    return Html(
        Head(
            Title("Reset Password | OpenData.London"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            Style("""
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { background: #080a0f; font-family: 'Inter', sans-serif; min-height: 100vh; display: flex; flex-direction: column; }
                .auth-topbar { display: flex; align-items: center; justify-content: space-between; padding: 18px 40px; border-bottom: 1px solid rgba(255,255,255,0.06); }
                .auth-brand { font-size: 17px; font-weight: 700; color: #fff; text-decoration: none; }
                .auth-brand span { color: #0284C7; }
                .auth-wrapper { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }
                .auth-card { width: 100%; max-width: 420px; }
                .auth-heading { font-size: 26px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.5px; margin-bottom: 6px; text-align: center; }
                .auth-subheading { font-size: 14px; color: #64748B; text-align: center; margin-bottom: 32px; line-height: 1.6; }
                .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
                .form-label { font-size: 13px; font-weight: 500; color: #CBD5E1; }
                .form-input { width: 100%; background: #020617; border: 1px solid rgba(148,163,184,0.18); color: #F8FAFC; padding: 11px 14px; border-radius: 7px; font-family: 'Inter', sans-serif; font-size: 14px; transition: border-color 0.2s; }
                .form-input:focus { outline: none; border-color: #0284C7; }
                .form-input::placeholder { color: #334155; }
                .auth-submit-btn { width: 100%; background: #0284C7; color: #020617; font-weight: 700; font-size: 14px; padding: 12px; border: none; border-radius: 7px; cursor: pointer; font-family: 'Inter', sans-serif; transition: opacity 0.2s; }
                .auth-submit-btn:hover { opacity: 0.88; }
                .auth-message { min-height: 20px; text-align: center; font-size: 13px; margin-top: 12px; }
                .error-text { color: #EF4444; }
                .success-text { color: #10B981; }
                .auth-card-footer { text-align: center; font-size: 13px; color: #475569; margin-top: 24px; }
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
                    H1("Reset your password", cls="auth-heading"),
                    P("Enter your email and we'll send you a link to reset your password.", cls="auth-subheading"),
                    Form(
                        Div(
                            Label("Email", fr="email", cls="form-label"),
                            Input(type="email", id="email", name="email", required=True,
                                  placeholder="name@company.com", cls="form-input"),
                            cls="form-group"
                        ),
                        Button("Send Reset Link", type="submit", cls="auth-submit-btn"),
                        hx_post="/forgot-password",
                        hx_target="#forgot-message"
                    ),
                    Div(id="forgot-message", cls="auth-message"),
                    Div(A("← Back to sign in", href="/login"), cls="auth-card-footer"),
                    cls="auth-card"
                ),
                cls="auth-wrapper"
            )
        )
    )


def ResetPasswordPage(token: str = ""):
    pw_pattern = password_policy_html_pattern()
    pw_title = "At least 8 characters, including one special character (not a letter or digit)."
    return Html(
        Head(
            Title("Set New Password | OpenData.London"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            Style("""
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { background: #080a0f; font-family: 'Inter', sans-serif; min-height: 100vh; display: flex; flex-direction: column; }
                .auth-topbar { display: flex; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(255,255,255,0.06); }
                .auth-brand { font-size: 17px; font-weight: 700; color: #fff; text-decoration: none; }
                .auth-brand span { color: #0284C7; }
                .auth-wrapper { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }
                .auth-card { width: 100%; max-width: 420px; }
                .auth-heading { font-size: 26px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.5px; margin-bottom: 6px; text-align: center; }
                .auth-subheading { font-size: 14px; color: #64748B; text-align: center; margin-bottom: 32px; }
                .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
                .form-label { font-size: 13px; font-weight: 500; color: #CBD5E1; }
                .form-input { width: 100%; background: #020617; border: 1px solid rgba(148,163,184,0.18); color: #F8FAFC; padding: 11px 14px; border-radius: 7px; font-family: 'Inter', sans-serif; font-size: 14px; transition: border-color 0.2s; }
                .form-input:focus { outline: none; border-color: #0284C7; }
                .form-input::placeholder { color: #334155; }
                .form-hint { font-size: 12px; color: #64748B; line-height: 1.45; margin-top: 4px; }
                .auth-submit-btn { width: 100%; background: #0284C7; color: #020617; font-weight: 700; font-size: 14px; padding: 12px; border: none; border-radius: 7px; cursor: pointer; font-family: 'Inter', sans-serif; transition: opacity 0.2s; }
                .auth-submit-btn:hover { opacity: 0.88; }
                .auth-message { min-height: 20px; text-align: center; font-size: 13px; margin-top: 12px; }
                .error-text { color: #EF4444; }
                .success-text { color: #10B981; }
            """)
        ),
        Body(
            Div(
                A("OpenData", Span(".London"), href="https://www.opendata.london", cls="auth-brand"),
                cls="auth-topbar"
            ),
            Div(
                Div(
                    H1("Set new password", cls="auth-heading"),
                    P("Choose a strong password for your account.", cls="auth-subheading"),
                    Form(
                        Input(type="hidden", name="token", value=token),
                        Div(
                            Label("New Password", fr="password", cls="form-label"),
                            Input(
                                type="password",
                                id="password",
                                name="password",
                                required=True,
                                minlength=8,
                                pattern=pw_pattern,
                                title=pw_title,
                                placeholder="8+ characters, 1 special char",
                                cls="form-input",
                            ),
                            P(PASSWORD_POLICY_HINT, cls="form-hint"),
                            cls="form-group"
                        ),
                        Div(
                            Label("Confirm Password", fr="confirm_password", cls="form-label"),
                            Input(type="password", id="confirm_password", name="confirm_password", required=True,
                                  placeholder="Repeat password", cls="form-input"),
                            cls="form-group"
                        ),
                        Button("Update Password", type="submit", cls="auth-submit-btn"),
                        hx_post="/reset-password",
                        hx_target="#reset-message"
                    ),
                    Div(id="reset-message", cls="auth-message"),
                    cls="auth-card"
                ),
                cls="auth-wrapper"
            )
        )
    )
