from fasthtml.common import *
from app.components import odl_navbar

def login_form():
    return Div(
        H2("Sign In", cls="auth-title"),
        P("Enter your credentials to access the London Database.", cls="auth-subtitle"),
        Form(
             Div(
                 Label("Email", fr="email", cls="form-label"),
                 Input(type="email", id="email", name="email", required=True, placeholder="name@company.com", cls="form-input"),
                 cls="form-group"
             ),
             Div(
                 Label("Password", fr="password", cls="form-label"),
                 Input(type="password", id="password", name="password", required=True, placeholder="••••••••", cls="form-input"),
                 cls="form-group"
             ),
             Button("Sign In", type="submit", cls="auth-btn"),
             hx_post="/login",
             hx_target="#auth-message",
             cls="auth-form"
        ),
        Div(id="auth-message", cls="auth-message"),
        Div(
            Span("Don't have an account? ", cls="auth-text"),
            A("Request Access", href="/register", cls="auth-link"),
            cls="auth-footer"
        ),
        cls="auth-card"
    )

def register_form():
    return Div(
        H2("Create Account", cls="auth-title"),
        P("Register for access to the London Database.", cls="auth-subtitle"),
        Form(
             Div(
                 Label("Email", fr="email", cls="form-label"),
                 Input(type="email", id="email", name="email", required=True, placeholder="name@company.com", cls="form-input"),
                 cls="form-group"
             ),
             Div(
                 Label("Password", fr="password", cls="form-label"),
                 Input(type="password", id="password", name="password", required=True, placeholder="••••••••", cls="form-input"),
                 cls="form-group"
             ),
             Button("Register", type="submit", cls="auth-btn"),
             hx_post="/register",
             hx_target="#auth-message",
             cls="auth-form"
        ),
        Div(id="auth-message", cls="auth-message"),
        Div(
            Span("Already have an account? ", cls="auth-text"),
            A("Sign In", href="/login", cls="auth-link"),
            cls="auth-footer"
        ),
        cls="auth-card"
    )

def AuthPage(mode="login"):
    
    auth_style = Style("""
        .auth-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 65px); /* Minus navbar */
            background: #0B1120; /* Dark background matching app */
        }
        .auth-card {
            background: #0F172A;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 12px;
            padding: 40px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
        }
        .auth-title {
            font-size: 24px;
            font-weight: 700;
            color: #F8FAFC;
            margin: 0 0 8px 0;
            letter-spacing: -0.5px;
        }
        .auth-subtitle {
            color: #94A3B8;
            font-size: 14px;
            margin: 0 0 32px 0;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            color: #E2E8F0;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .form-input {
            width: 100%;
            background: #020617;
            border: 1px solid rgba(148, 163, 184, 0.2);
            color: #F8FAFC;
            padding: 10px 16px;
            border-radius: 6px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            transition: border-color 0.2s;
            box-sizing: border-box;
        }
        .form-input:focus {
            outline: none;
            border-color: #29b5e8;
        }
        .auth-btn {
            width: 100%;
            background: #29b5e8;
            color: #020617;
            font-weight: 600;
            font-size: 14px;
            padding: 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: opacity 0.2s;
            margin-top: 8px;
            font-family: 'Inter', sans-serif;
        }
        .auth-btn:hover {
            opacity: 0.9;
        }
        .auth-footer {
            margin-top: 24px;
            text-align: center;
            font-size: 13px;
        }
        .auth-text {
            color: #94A3B8;
        }
        .auth-link {
            color: #29b5e8;
            text-decoration: none;
            font-weight: 500;
        }
        .auth-link:hover {
            text-decoration: underline;
        }
        .auth-message {
            margin-top: 16px;
            text-align: center;
            font-size: 14px;
            min-height: 20px; /* reserve space */
        }
        .error-text {
            color: #EF4444;
        }
        .success-text {
            color: #10B981;
        }
    """)
    
    form_component = login_form() if mode == "login" else register_form()
    
    return Html(
        Head(
            Title("Authentication | ODL App"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            auth_style,
            Script(src="https://unpkg.com/htmx.org@1.9.10")
        ),
        Body(
            odl_navbar(user=None), # Nav without sidebar/actions for auth page
            Div(
                form_component,
                cls="auth-container"
            ),
            style="margin: 0; padding: 0; background: #0B1120; font-family: 'Inter', sans-serif;"
        )
    )
