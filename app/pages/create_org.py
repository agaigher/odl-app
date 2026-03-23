from fasthtml.common import *


def CreateOrgPage():
    return Html(
        Head(
            Title("Create Organisation | OpenData.London"),
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
                .auth-heading { font-size: 26px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.5px; margin-bottom: 6px; }
                .auth-subheading { font-size: 14px; color: #64748B; margin-bottom: 32px; line-height: 1.6; }
                .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
                .form-label { font-size: 13px; font-weight: 500; color: #CBD5E1; }
                .form-hint { font-size: 12px; color: #475569; margin-top: 3px; }
                .form-input { width: 100%; background: #020617; border: 1px solid rgba(148,163,184,0.18); color: #F8FAFC; padding: 11px 14px; border-radius: 7px; font-family: 'Inter', sans-serif; font-size: 14px; transition: border-color 0.2s; }
                .form-input:focus { outline: none; border-color: #0284C7; }
                .form-input::placeholder { color: #334155; }
                .form-input[readonly] { color: #64748B; cursor: default; }
                .auth-submit-btn { width: 100%; background: #0284C7; color: #020617; font-weight: 700; font-size: 14px; padding: 12px; border: none; border-radius: 7px; cursor: pointer; font-family: 'Inter', sans-serif; transition: opacity 0.2s; margin-top: 8px; }
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
                    H1("Create an organisation", cls="auth-heading"),
                    P("Organisations let you manage team access and shared data permissions in one place.", cls="auth-subheading"),
                    Form(
                        Div(
                            Label("Organisation name", fr="org_name", cls="form-label"),
                            Input(type="text", id="org_name", name="org_name", required=True,
                                  placeholder="e.g. Acme Analytics", cls="form-input",
                                  oninput="updateSlug(this.value)"),
                            cls="form-group"
                        ),
                        Div(
                            Label("URL slug", fr="slug", cls="form-label"),
                            Input(type="text", id="slug", name="slug", required=True,
                                  placeholder="acme-analytics", cls="form-input"),
                            P("app.opendata.london/org/your-slug", cls="form-hint", id="slug-preview"),
                            cls="form-group"
                        ),
                        Button("Create Organisation", type="submit", cls="auth-submit-btn"),
                        hx_post="/create-org",
                        hx_target="#org-message"
                    ),
                    Div(id="org-message", cls="auth-message"),
                    Div(A("← Back to dashboard", href="/"), cls="auth-card-footer"),
                    cls="auth-card"
                ),
                cls="auth-wrapper"
            ),
            Script("""
                function slugify(text) {
                    return text.toLowerCase()
                        .replace(/[^a-z0-9\\s-]/g, '')
                        .trim()
                        .replace(/\\s+/g, '-')
                        .replace(/-+/g, '-');
                }
                function updateSlug(name) {
                    const slug = slugify(name);
                    document.getElementById('slug').value = slug;
                    document.getElementById('slug-preview').textContent =
                        'app.opendata.london/org/' + (slug || 'your-slug');
                }
            """)
        )
    )
