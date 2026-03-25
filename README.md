# ODL App — OpenData.London Platform

FastHTML/Starlette web application for the OpenData.London data platform.
Deployed to Vercel as a Python serverless function.

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd odl-app

# 2. Create a virtual environment
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy .env.example to .env and fill in your keys (see Environment Variables below)

# 5. Run the dev server
python main.py
# App is now at http://localhost:5002
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon/public key (used for client auth) |
| `SUPABASE_SERVICE_KEY` | Yes | Supabase service role key (used for server-side DB access) |
| `APP_URL` | Yes | Public app URL, e.g. `https://app.opendata.london` |
| `SESSION_SECRET` | Yes | Secret key for session cookies |
| `STRIPE_API_KEY` | No | Stripe secret key for billing |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook signing secret |
| `RESEND_API_KEY` | No | Resend API key for transactional email |
| `RESEND_FROM` | No | Sender email for Resend, e.g. `noreply@opendata.london` |
| `ANTHROPIC_API_KEY` | No | Anthropic key for AI-powered catalog search |
| `SNOWFLAKE_ACCOUNT` | No | Snowflake account identifier for OAuth |
| `SNOWFLAKE_CLIENT_ID` | No | Snowflake OAuth client ID |
| `SNOWFLAKE_CLIENT_SECRET` | No | Snowflake OAuth client secret |

## Project Structure

```
odl-app/
  main.py                  # Entry point — imports app, calls serve()
  api/index.py             # Vercel serverless entry (re-exports app)
  app/
    __init__.py            # App factory — creates FastHTML app, registers all routes
    config.py              # All environment variables, loaded once
    auth/                  # Authentication & OAuth
      client.py            #   Supabase GoTrue client singleton
      middleware.py         #   before() middleware, get_user_id() helper
      routes.py            #   Login, register, logout, OAuth, password reset
    catalog/               # Data catalog
      data.py              #   Dataset seed definitions + seed_catalog()
      routes.py            #   Catalog browsing, search, AI search, favourites
    integrations/          # Data integrations
      routes.py            #   CRUD, toggle datasets in/out of integrations
    billing/               # Billing & payments
      routes.py            #   Billing page, checkout, spend-cap, emails, address
      stripe_webhook.py    #   Stripe webhook handler (isolated)
    orgs/                  # Organisations
      routes.py            #   Create, list, switch, open, detail
    projects/              # Projects
      routes.py            #   Create, list, select
    team/                  # Team management
      routes.py            #   Members, invite, role change, remove, resend, revoke
      invite.py            #   Invite accept/confirm flow
    settings/              # Organisation settings
      routes.py            #   General, avatar, rename, transfer, delete, billing, SSO
    api_v1/                # Public REST API
      routes.py            #   POST /api/v1/query
    dashboard/             # Dashboard & misc pages
      routes.py            #   Home, project overview, usage, docs, queries, robots.txt
    db/                    # Database access layer (Supabase REST)
      client.py            #   Core CRUD: db_insert, db_select, db_patch, db_delete
      storage.py           #   Supabase Storage uploads
      auth_admin.py        #   Admin invite link generation
    ui/                    # Shared UI components & styles
      components.py        #   Navbar, sidebar, page_layout, icons
      styles.py            #   CSS: get_app_style, get_shared_style
    email.py               # Transactional email via Resend
    pages/                 # Page-level view components (FastHTML)
      auth.py, billing.py, catalog.py, dashboard.py, dataset.py, ...
  scripts/                 # Offline ops scripts
    import_submissions.py
  data-submitted/          # Submitted CSV data files
  launch-planning/         # Internal launch notes
```

## How It Works

Each feature area (auth, catalog, billing, etc.) has its own folder with a `routes.py`
that exports a `register(rt)` function. The app factory in `app/__init__.py` calls each
`register(rt)` to wire up all endpoints on the single FastHTML app.

Page view components live in `app/pages/` and are imported by the route handlers.
Shared layout (navbar, sidebar, `page_layout()`) lives in `app/ui/components.py`.

All database access goes through `app/db/` which wraps Supabase's PostgREST API.

## Deployment

The app deploys to **Vercel** via `vercel.json`, which rewrites all requests to
`api/index.py`. That file simply does `from main import app`.

## Tech Stack

- **Python 3.12** with **FastHTML** (Starlette-based)
- **Supabase** — auth, database (PostgREST), storage
- **Stripe** — billing and payments
- **Resend** — transactional email
- **Anthropic** — AI catalog search
- **HTMX** — client-side interactivity
