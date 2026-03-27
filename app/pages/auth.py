from fasthtml.common import *

from app.auth.password_policy import PASSWORD_POLICY_HINT, password_policy_html_pattern
from app.ui.styles import get_critical_canvas_style, get_focus_ring_reset_style


def AuthPage(mode="login", login_error: str = ""):

    auth_style = Style("""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body.auth-page {
            /* Same canvas as logged-in app — no blue wash */
            background: #080a0f;
            font-family: 'Inter', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* ── Top bar ── */
        .auth-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px 40px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .auth-brand {
            font-size: 17px;
            font-weight: 700;
            color: #fff;
            text-decoration: none;
            letter-spacing: -0.3px;
        }
        .auth-brand span { color: #94a3b8; font-weight: 500; }
        .auth-topbar-link {
            font-size: 13px;
            color: #94A3B8;
            text-decoration: none;
        }
        .auth-topbar-link a {
            color: #7dd3fc;
            font-weight: 500;
            text-decoration: none;
        }
        .auth-topbar-link a:hover { text-decoration: underline; }

        /* ── Centered card ── */
        .auth-wrapper {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
        }
        .auth-card {
            width: 100%;
            max-width: 420px;
        }

        /* ── Heading ── */
        .auth-heading {
            font-size: 26px;
            font-weight: 600;
            font-family: 'Space Grotesk', system-ui, sans-serif;
            color: #F8FAFC;
            letter-spacing: -0.04em;
            margin-bottom: 6px;
            text-align: center;
        }
        .auth-subheading {
            font-size: 14px;
            color: #64748B;
            text-align: center;
            margin-bottom: 20px;
        }

        .auth-free-highlight {
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 24px;
            padding: 10px 16px;
            border-radius: 8px;
            background: rgba(2, 132, 199, 0.14);
            border: 1px solid rgba(2, 132, 199, 0.45);
            font-size: 13px;
            font-weight: 600;
            color: #7dd3fc;
            line-height: 1.4;
            letter-spacing: 0.01em;
        }

        /* ── OAuth buttons ── */
        .oauth-stack {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 24px;
        }
        .oauth-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            padding: 11px 16px;
            border-radius: 8px;
            border: 1px solid rgba(148,163,184,0.2);
            background: rgba(255,255,255,0.04);
            color: #E2E8F0;
            font-size: 14px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.2s, border-color 0.2s;
        }
        .oauth-btn:hover {
            background: rgba(255,255,255,0.08);
            border-color: rgba(148,163,184,0.35);
        }
        .oauth-btn svg { flex-shrink: 0; }
        .oauth-btn.snowflake-btn {
            border-color: rgba(2,132,199,0.35);
            color: #7dd3fc;
        }
        .oauth-btn.snowflake-btn:hover {
            background: rgba(2,132,199,0.1);
            border-color: rgba(2,132,199,0.45);
        }

        /* ── Divider ── */
        .auth-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
        }
        .auth-divider-line {
            flex: 1;
            height: 1px;
            background: rgba(148,163,184,0.15);
        }
        .auth-divider-text {
            font-size: 12px;
            color: #475569;
            white-space: nowrap;
        }

        /* ── Form ── */
        .auth-form { display: flex; flex-direction: column; gap: 16px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        .form-label {
            font-size: 13px;
            font-weight: 500;
            color: #CBD5E1;
        }
        .form-input {
            width: 100%;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(148,163,184,0.15);
            color: #F8FAFC;
            padding: 11px 14px;
            border-radius: 7px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .form-input:focus {
            outline: none;
            border-color: #0284C7;
        }
        .form-input::placeholder { color: #334155; }

        .form-hint {
            font-size: 12px;
            color: #64748B;
            line-height: 1.45;
        }

        .forgot-link {
            font-size: 12px;
            color: #7dd3fc;
            text-decoration: none;
            text-align: right;
            margin-top: -8px;
        }
        .forgot-link:hover { text-decoration: underline; }

        .auth-submit-btn {
            width: 100%;
            background: #0284C7;
            color: #ffffff;
            font-weight: 600;
            font-size: 14px;
            padding: 12px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            transition: opacity 0.2s;
            margin-top: 4px;
        }
        .auth-submit-btn:hover { opacity: 0.88; }

        /* ── Message ── */
        .auth-message {
            min-height: 20px;
            text-align: center;
            font-size: 13px;
            margin-top: 12px;
        }
        .error-text { color: #EF4444; }
        .success-text { color: #10B981; }

        .auth-alert {
            display: block;
            padding: 12px 14px;
            border-radius: 8px;
            border: 1px solid rgba(239, 68, 68, 0.35);
            background: rgba(239, 68, 68, 0.08);
            text-align: left;
            line-height: 1.45;
        }
        .auth-alert a {
            color: #7dd3fc;
            font-weight: 600;
            text-decoration: none;
        }
        .auth-alert a:hover { text-decoration: underline; }

        /* ── Footer ── */
        .auth-card-footer {
            text-align: center;
            font-size: 13px;
            color: #475569;
            margin-top: 24px;
        }
        .auth-card-footer a {
            color: #7dd3fc;
            font-weight: 500;
            text-decoration: none;
        }
        .auth-card-footer a:hover { text-decoration: underline; }

        /* ── Org divider ── */
        .org-link-row {
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: #475569;
            padding-top: 20px;
            border-top: 1px solid rgba(148,163,184,0.1);
        }
        .org-link-row a {
            color: #7dd3fc;
            font-weight: 500;
            text-decoration: none;
        }
        .org-link-row a:hover { text-decoration: underline; }
    """)

    # ── SVG icons ──
    google_icon = """<svg width="18" height="18" viewBox="0 0 18 18"><path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"/><path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/><path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707s.102-1.167.282-1.707V4.961H.957C.347 6.175 0 7.55 0 9s.348 2.825.957 4.039l3.007-2.332z"/><path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z"/></svg>"""

    github_icon = """<svg width="18" height="18" viewBox="0 0 24 24" fill="#fff"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.298 24 12c0-6.63-5.37-12-12-12z"/></svg>"""

    snowflake_icon = """<svg width="18" height="18" viewBox="0 0 24 24" fill="#0284C7"><path d="M12 2l1.5 2.6-1.5.866V8l2-1.155 1-1.732 1.5.866-1 1.732L13.5 8.732 16 10.155l2.5-1.443.75 1.299L17 11.299V14l1.5-.866 1-1.732 1.5.866-1 1.732-1.5.866L20 17.4l-1.5.866-.5-.866-2 1.155v2.31l1.5.866-.75 1.299L15 22.164 13.5 23.03 12 22.164l-1.5.866L9 22.164 7.5 23.03 6 22.164l.75-1.299 1.5-.866v-2.31l-2-1.155-.5.866L4 16.534l1.5-2.6 1.5.866V11.3l-2.25-1.3.75-1.299L8 10.155l2.5-1.443-1.5-.868-1-1.732 1-.577 1 1.732 2 1.155V5.466l-1.5-.866L11.5 2H12z"/></svg>"""

    is_login = mode == "login"

    topbar_right = Div(
        "Don't have an account? " if is_login else "Already have an account? ",
        A("Sign up" if is_login else "Sign in", href="/register" if is_login else "/login"),
        cls="auth-topbar-link"
    )

    oauth_buttons = Div(
        A(
            NotStr(google_icon), "Continue with Google",
            href="/auth/google", cls="oauth-btn"
        ),
        A(
            NotStr(github_icon), "Continue with GitHub",
            href="/auth/github", cls="oauth-btn"
        ),
        A(
            NotStr(snowflake_icon), "Continue with Snowflake",
            href="/auth/snowflake", cls="oauth-btn snowflake-btn"
        ),
        cls="oauth-stack"
    )

    divider = Div(
        Div(cls="auth-divider-line"),
        Span("or continue with email", cls="auth-divider-text"),
        Div(cls="auth-divider-line"),
        cls="auth-divider"
    )

    pw_pattern = password_policy_html_pattern()
    pw_title = "At least 8 characters, including one special character (not a letter or digit)."

    if is_login:
        form = Form(
            Div(
                Label("Email", fr="email", cls="form-label"),
                Input(type="email", id="email", name="email", required=True,
                      placeholder="name@company.com", cls="form-input"),
                cls="form-group"
            ),
            Div(
                Label("Password", fr="password", cls="form-label"),
                Input(
                    type="password",
                    id="password",
                    name="password",
                    required=True,
                    minlength=8,
                    pattern=pw_pattern,
                    title=pw_title,
                    placeholder="••••••••",
                    cls="form-input",
                ),
                P(PASSWORD_POLICY_HINT, cls="form-hint"),
                cls="form-group"
            ),
            A("Forgot password?", href="/forgot-password", cls="forgot-link"),
            Button("Sign In", type="submit", cls="auth-submit-btn"),
            hx_post="/login",
            hx_target="#auth-message",
            cls="auth-form"
        )
        heading = "Welcome back"
        subheading = "Sign in to your OpenData.London account"
        footer = Div(
            "Don't have an account? ", A("Sign up", href="/register"),
            cls="auth-card-footer"
        )
    else:
        form = Form(
            Div(
                Label("Email", fr="email", cls="form-label"),
                Input(type="email", id="email", name="email", required=True,
                      placeholder="name@company.com", cls="form-input"),
                cls="form-group"
            ),
            Div(
                Label("Password", fr="password", cls="form-label"),
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
            Button("Create Account", type="submit", cls="auth-submit-btn"),
            hx_post="/register",
            hx_target="#auth-message",
            cls="auth-form"
        )
        heading = "Create your account"
        subheading = "Start accessing London's open data platform"
        footer = Div(
            "Already have an account? ", A("Sign in", href="/login"),
            cls="auth-card-footer"
        )

    org_row = Div(
        "Setting up for a team? ", A("Create an organisation →", href="/create-org"),
        cls="org-link-row"
    )

    free_highlight = Div("It's free to create an account", cls="auth-free-highlight")

    login_alert = None
    if is_login and login_error == "email_not_confirmed":
        login_alert = Div(
            "Your email address must be confirmed before you can sign in with this account.",
            cls="error-text auth-alert",
            role="alert",
            style="margin-bottom: 20px;",
        )

    card_inner = [
        H1(heading, cls="auth-heading"),
        P(subheading, cls="auth-subheading"),
        free_highlight,
        oauth_buttons,
        divider,
        form,
        Div(id="auth-message", cls="auth-message"),
        footer,
        org_row,
    ]
    if login_alert:
        card_inner.insert(0, login_alert)

    return Html(
        Head(
            Title("Sign In | OpenData.London" if is_login else "Create Account | OpenData.London"),
            get_critical_canvas_style(bg="#080a0f", fg="#f8fafc"),
            Meta(name="theme-color", content="#080a0f"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            auth_style,
            get_focus_ring_reset_style(),
            Script(src="https://unpkg.com/htmx.org@1.9.10")
        ),
        Body(
            # Top bar
            Div(
                A("OpenData", Span(".London"), href="https://www.opendata.london", cls="auth-brand"),
                topbar_right,
                cls="auth-topbar"
            ),
            # Card
            Div(
                Div(*card_inner, cls="auth-card"),
                cls="auth-wrapper"
            ),
            cls="auth-page"
        )
    )
