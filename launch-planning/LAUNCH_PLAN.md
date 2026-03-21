# OpenData.London — Launch Plan

**Last updated:** 2026-03-21
**Status:** Pre-launch
**Goal:** Onboard first paying customers

---

## Current state summary

The platform has a working auth and data catalogue shell deployed at `app.opendata.london`. Authentication (email/password, Google, GitHub, Snowflake OAuth), organisations, and the catalogue UI are complete. The critical gap is that the underlying data does not exist in a queryable form — no Snowflake database, no ingestion pipelines, no working API. Everything below flows from that.

---

## Phase 1 — Make the product real
**Target: before any customer demo**

### 1.1 Ingest the first real dataset into Snowflake

The London Database needs at least one complete, live, queryable dataset before anything else matters. Companies House is the right starting point: it is free, well-documented, updated daily, commercially valuable, and the bulk download is straightforward.

Tasks:
- Set up the `LONDON_DB` Snowflake database with a clean schema (`RAW`, `CLEAN`, `PUBLIC` layers)
- Write a Python ingestion script for Companies House bulk data (download, parse, load)
- Schedule it to run daily (GitHub Actions or Snowflake Tasks)
- Validate the data: row counts, null rates, basic sanity checks
- Document the schema in `catalog_data.py` with real column names and real sample rows

Acceptance: a Snowflake query against `LONDON_DB.PUBLIC.UK_COMPANIES_HOUSE` returns real data.

### 1.2 Build the data query API

Currently `/api/v1/...` does not exist. We need a working endpoint before API key access means anything.

Tasks:
- `GET /api/v1/{slug}` — query a dataset with `limit`, `offset`, basic `filter` params
- Connect to Snowflake via `snowflake-connector-python` using a service account
- API key validation middleware: hash the incoming key, check against `api_keys` table, verify the user has `dataset_access` for the requested slug
- Standardised JSON response: `{ data: [...], total: N, page: N, per_page: N }`
- Standardised error responses: 401 (bad key), 403 (no access), 404 (no dataset), 429 (rate limited), 500 (query failed)
- Rate limiting: per key, configurable per plan (e.g. 1000 req/day free, 100k/day paid)

### 1.3 Build real API key generation and management

The `/keys` page is a UI stub. No keys can currently be created.

Tasks:
- `api_keys` table in Supabase: `id, user_id, name, key_prefix, key_hash, dataset_slugs[], plan, created_at, last_used_at, revoked_at`
- Key generation: `odl_live_` prefix + 32 random bytes (base58 encoded), store only the SHA-256 hash
- Return the plaintext key exactly once at creation — never again
- UI: generate key with a name, copy to clipboard, see last used date, revoke
- Keys are scoped to specific datasets the user has access to (not global)

### 1.4 Build the Snowflake zero-copy share fulfillment workflow

Share requests land in `share_requests` and stop there. There is no way to fulfil them.

Tasks:
- Admin panel view: pending share requests table (user email, dataset slug, Snowflake account, requested date)
- Fulfillment checklist per request: Snowflake commands to run, checkbox to mark done
- On fulfillment: update `share_requests.status = 'fulfilled'`, set `fulfilled_at`, trigger email to customer
- Customer-facing status: dashboard shows "Pending", "Active" with setup instructions once fulfilled
- Later: automate via Snowflake Python connector (create the share programmatically)

### 1.5 Build the user dashboard

After login, users see the catalog with no personalisation. They need a home screen.

Tasks:
- `/dashboard` route (redirect from `/` post-login)
- Sections: "Your datasets" (active API + Snowflake access), "Pending requests", "API keys" (count + last used), "Organisation" (name + member count)
- Empty state for new users: single CTA — "Browse the catalog to request access"
- Quick actions: generate API key, browse catalog, view org settings

---

## Phase 2 — Make it operable
**Target: before charging real money**

### 2.1 Build the admin panel

There is no internal tool. You cannot manage the platform without editing Supabase tables directly.

Tasks:
- `/admin` route protected by an `is_admin` flag on the user profile
- Views:
  - Pending share requests (with fulfillment workflow — see 1.4)
  - All users: email, signup date, datasets accessed, org membership
  - All dataset access grants: who has access to what, when granted, API or Snowflake
  - Dataset management: edit title, description, status (live/coming soon/restricted) without a code deploy
  - CSV import: read from `data-submissions/`, preview, approve, insert into Supabase `datasets` table
- Actions:
  - Grant or revoke dataset access manually
  - Fulfill or reject share requests
  - Suspend a user account
  - Promote a user to admin

### 2.2 CSV import pipeline for researcher submissions

The researcher will submit CSVs to `data-submissions/`. There is no automated path to get them into the catalog.

Tasks:
- `scripts/import_submissions.py`: reads all CSVs in `data-submissions/`, parses `schema_fields` and `sample_rows` columns (pipe-delimited), upserts into Supabase `datasets` table on `slug` conflict
- Validates required fields before inserting, logs skipped rows
- Can be run manually or triggered from the admin panel (button: "Import pending submissions")
- Moves processed files to `data-submissions/imported/YYYY-MM-DD/` to avoid double-import

### 2.3 Transactional email

No product emails are sent beyond Supabase's built-in auth flows.

Tasks:
- Integrate Resend (Python SDK, simple, generous free tier)
- Set up sending domain: `noreply@opendata.london` (add SPF, DKIM, DMARC DNS records)
- Templates for:
  - Welcome email on first login
  - Share request received (confirmation to customer)
  - Share fulfilled (with Snowflake setup instructions)
  - API access granted
  - Organisation invite (supplement or replace Supabase's invite email)
  - Monthly usage summary (later)

### 2.4 Documentation

`/docs` is a blank white div.

Tasks:
- Getting started guide: sign up → browse catalog → request access → make your first API call
- API reference: endpoint list, parameters, response format, error codes, rate limits
- Snowflake guide: how to accept a share, explore `LONDON_DB`, write your first query
- Dataset pages: link through to the catalog detail page for field definitions
- Keep docs in-app at `/docs` (FastHTML rendered from markdown) or host on a subdomain

### 2.5 Legal pages

Required before onboarding any paying customer.

- **Privacy Policy**: what data we collect, why, how long we keep it, who we share it with, GDPR rights
- **Terms of Service**: acceptable use, liability, payment terms, termination, governing law (England & Wales)
- **Acceptable Use Policy**: what users cannot do with the data (scraping restrictions, redistribution, rate limit abuse)
- **Data Processing Agreement (DPA)**: required for B2B customers who are themselves data controllers — covers GDPR Article 28 obligations
- Add links to footer on both odl-web and odl-app

Have these reviewed by a solicitor with data law experience before publishing, especially the DPA.

### 2.6 Error pages

- Custom 404 page: "Page not found" with navigation back to dashboard or catalog
- Custom 500 page: "Something went wrong" with a support contact
- Both should use the app's design language, not Vercel's default error screen

---

## Phase 3 — Make it commercial
**Target: first paying customer**

### 3.1 Billing and payments

No pricing exists and no payment can be taken.

Tasks:
- Define pricing model (recommendation below)
- Stripe integration: checkout session, webhook to update user plan in Supabase, customer portal for self-service billing management
- Plan-gated access: free tier (limited datasets, 100 API calls/day), professional tier, enterprise (custom)
- Entitlement system: plan stored on user profile, API middleware checks plan before serving data

Recommended starting pricing model:
- **Free**: access to 1–2 preview datasets, 100 API calls/day, no Snowflake shares
- **Professional (£299/month)**: up to 5 datasets, 50k API calls/day, 1 Snowflake share
- **Enterprise (custom)**: all datasets, unlimited API, multiple Snowflake shares, DPA, SLA

### 3.2 Expand the data catalogue

Phase 1 covers Companies House. To be commercially viable at launch you need at least 3–5 datasets that work end-to-end. Recommended priority order based on commercial demand:

1. UK Companies House (directors, filings, charges) — ingestion in Phase 1
2. FCA Regulatory Register — free download, high compliance use case
3. Land Registry HMLR Price Paid Data — free, very high demand
4. TfL API feeds — free, real-time, differentiating
5. London Planning Applications (aggregated from borough portals) — more complex, high value

### 3.3 Monitoring and reliability

Currently there is no visibility into errors or downtime.

Tasks:
- Sentry: error tracking on both odl-web and odl-app. Free tier sufficient to start.
- Uptime monitoring: Better Uptime or similar — ping `app.opendata.london/health` every minute, alert on failure
- Snowflake query monitoring: log query times, flag slow queries (>5s)
- Vercel analytics: enable for basic traffic visibility
- `GET /health` endpoint: returns 200 with app version, DB connectivity check, Snowflake ping

### 3.4 Staging environment

Currently changes go straight to production on every push to `main`.

Tasks:
- Create a `staging` branch
- Set up a separate Vercel project pointing at `staging.app.opendata.london`
- Separate Supabase project for staging (so schema changes can be tested before hitting production data)
- Deployment process: `staging` → review → merge to `main` → auto-deploy to production

---

## Security — gaps to close before launch

### Authentication and session security

- [ ] Session secret is already in an env var — confirm it is a long random string (32+ bytes), not a dev placeholder
- [ ] Implement CSRF protection on all state-changing POST endpoints (FastHTML does not include this by default)
- [ ] Set `Secure`, `HttpOnly`, `SameSite=Lax` on session cookies — verify Vercel config
- [ ] Implement login rate limiting: max 10 attempts per IP per 15 minutes (Supabase has some built-in; supplement at app layer)
- [ ] Ensure password reset tokens expire (Supabase default is 1 hour — confirm this is set)
- [ ] OAuth state parameter: verify that the OAuth flows validate the `state` param to prevent CSRF on callback

### API security

- [ ] API keys stored as SHA-256 hashes only — never log or expose plaintext keys after creation
- [ ] API key prefix (`odl_live_`) is safe to log — only hash the full key
- [ ] All API endpoints must validate `Content-Type` on POST requests
- [ ] Snowflake service account used by the query API should have read-only access, scoped to `LONDON_DB.PUBLIC` only — never use ACCOUNTADMIN
- [ ] Parameterise all Snowflake queries — never interpolate user input directly into SQL strings

### Infrastructure security

- [ ] All env vars (Supabase keys, Snowflake credentials, session secret) are in Vercel env vars — confirm none are committed to the repo
- [ ] `.gitignore` covers `.env`, `.sesskey`, `data/`, `__pycache__` — already done, verify it is comprehensive
- [ ] Enable Vercel's DDoS protection (included on all plans)
- [ ] Set security headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy` (strict — no inline scripts except HTMX)
- [ ] Dependency vulnerability scanning: add `pip-audit` to CI or run manually before each release
- [ ] Rotate the Supabase service key and session secret periodically — document the rotation process

### Data security

- [ ] Supabase RLS is enabled on all tables — verify each table has policies, none are accidentally open
- [ ] The `service_role` key (which bypasses RLS) is used only in server-side admin operations — never exposed to the client
- [ ] Snowflake shares are read-only by design — confirm the `LONDON_DB` objects shared are granted `SELECT` only
- [ ] No PII from user records (emails, names) is ever included in API query responses or logs
- [ ] Define a data retention policy: how long do we keep `dataset_access`, `share_requests`, `api_keys` after revocation?

---

## Compliance — requirements before charging customers

### GDPR / UK GDPR

The platform processes personal data (user email addresses, and some datasets like Companies House contain personal data — director names, addresses). UK GDPR applies.

- [ ] **ICO registration**: register with the Information Commissioner's Office as a data controller. Required for any UK business processing personal data. Fee is £40–£60/year for small organisations. Do this immediately.
- [ ] **Lawful basis**: document the lawful basis for each type of data processing (legitimate interest for auth, contract for service delivery, etc.)
- [ ] **Privacy Policy**: must be published before launch (see Phase 2.5)
- [ ] **Cookie consent**: any cookies beyond strictly necessary session cookies require explicit consent. Implement a cookie banner on both odl-web and odl-app.
- [ ] **Right to erasure**: implement a "Delete my account" flow that removes the user from Supabase auth and all related Supabase tables (`profiles`, `dataset_access`, `share_requests`, `memberships`)
- [ ] **Data breach notification**: internal process — if a breach occurs we have 72 hours to notify the ICO. Document who is responsible and how to notify.
- [ ] **Sub-processor agreements**: ensure Supabase, Vercel, and any email provider have signed DPAs. Supabase and Vercel both offer these — download and retain copies.
- [ ] **Data minimisation**: do not collect data you do not need. Current signup only requires email — good.

### Dataset licensing

Every dataset in the catalogue must have a verified licence that permits redistribution and/or commercial use.

- [ ] For each dataset, document the exact licence in `catalog_data.py` and the catalogue UI
- [ ] Open Government Licence (OGL v3) — permits commercial use and redistribution with attribution. Most UK government data falls under this.
- [ ] Verify attribution requirements for each OGL dataset — some require explicit attribution in downstream products
- [ ] Flag any datasets that are not OGL or CC-licensed — these require individual licence negotiation before publishing
- [ ] Do not ingest or redistribute any dataset where the licence is unclear or restrictive. When in doubt, do not include until clarified.
- [ ] Consider whether our API constitutes "redistribution" under each licence (it does) — confirm all licences permit this use case

### Financial and commercial

- [ ] If taking payment, ensure Stripe handles PCI DSS compliance (it does, as long as you do not handle raw card data — always use Stripe's hosted checkout)
- [ ] Business registration: confirm the company is incorporated before signing any customer contracts
- [ ] If selling to enterprises, they will ask for your company registration number, VAT number, and proof of insurance — have these ready

---

## Technical debt to address before scaling

### Performance

- [ ] Cache the dataset catalogue in memory or Redis — it changes only on deploy, should not hit Supabase on every page load
- [ ] Paginate API responses — no unbounded queries
- [ ] Snowflake query timeout: set a maximum query execution time (30s) to prevent runaway queries consuming credits

### Code quality

- [ ] Remove the `/debug/catalog` endpoint before launch — it exposes internal state
- [ ] Remove all print-based error handling in `seed_catalog()` — use proper logging
- [ ] Validate all user-facing form inputs server-side (not just client-side)
- [ ] The Snowflake OAuth flow (`/auth/snowflake`) needs end-to-end testing — it is not yet verified working in production

### Missing pages

- [ ] `GET /health` — machine-readable health check endpoint
- [ ] 404 and 500 error pages
- [ ] `/docs` — full API documentation
- [ ] Account settings (`/settings`) — read/write `profiles` table
- [ ] Mobile responsiveness audit — the app and landing page need to work on phones

---

## Completion checklist

Mark items `[x]` as they are completed. Update the date next to each item when done.

### Phase 1 — Make the product real

- [ ] Ingest Companies House into Snowflake
- [ ] Data query API (`/api/v1/{slug}`)
- [ ] API key generation and management
- [ ] Snowflake share fulfillment workflow
- [ ] User dashboard

### Phase 2 — Make it operable

- [ ] Admin panel
- [ ] CSV import pipeline (researcher submissions)
- [ ] Transactional email (Resend)
- [ ] Documentation (`/docs`)
- [ ] Legal pages (ToS, Privacy Policy, AUP, DPA)
- [ ] Error pages (404, 500)

### Phase 3 — Make it commercial

- [ ] Billing and Stripe integration
- [ ] Expand to 3–5 datasets end-to-end
- [ ] Monitoring (Sentry, uptime, `/health` endpoint)
- [ ] Staging environment

### Compliance

- [ ] ICO registration (do this immediately — legally required)
- [ ] GDPR: cookie consent banner
- [ ] GDPR: right to erasure / delete account flow
- [ ] Dataset licence audit (verify each dataset permits commercial redistribution)
- [ ] Sub-processor DPAs signed (Supabase, Vercel, email provider)
- [ ] Business registration confirmed before first customer contract

### Security

- [ ] Security headers (`X-Frame-Options`, `CSP`, `X-Content-Type-Options`, etc.)
- [ ] CSRF protection on all POST endpoints
- [ ] API keys stored as SHA-256 hashes only
- [ ] Snowflake service account: read-only, scoped to `LONDON_DB.PUBLIC`
- [ ] Dependency vulnerability scanning (`pip-audit`)
- [ ] RLS audit: confirm every Supabase table has policies
- [ ] Login rate limiting confirmed working
- [ ] OAuth state parameter validation confirmed

### Technical debt

- [ ] Remove `/debug/catalog` endpoint
- [ ] Account settings page (`/settings` reads/writes `profiles` table)
- [ ] Mobile responsiveness audit
- [ ] Snowflake OAuth end-to-end test in production
- [ ] SPF / DKIM / DMARC DNS records for `opendata.london`
- [ ] Favicon and Open Graph meta tags on both odl-web and odl-app
- [ ] `robots.txt` to block indexing of authenticated routes
- [ ] Vercel spend limit set
- [ ] Snowflake resource monitor / spend alert set
- [ ] GitHub branch protection enabled on `main`
- [ ] Supabase backup strategy confirmed
- [ ] Incident response contact documented
