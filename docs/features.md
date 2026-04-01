# OpenData.London — Features Reference

What is built, what is not yet built, and the full specification for upcoming features.

---

## Core Principle

OpenData.London is a **data platform** that makes London's public datasets discoverable, queryable, and integrable — from a single interface, with a consistent API, across multiple data consumers (teams, tools, Snowflake pipelines).

The catalog is the single source of truth for what datasets exist. Integrations are the mechanism by which users subscribe to datasets and query them. The data layer (odl-data) runs independently and feeds Snowflake; the app layer (odl-app) surfaces it to users.

**Separation of concerns:**
- `odl-app` — web UI, auth, billing, catalog browsing, API surface for queries
- `odl-data` — ingestion, transforms, scheduling, local DuckDB warehouse, Snowflake export

---

## Target User Journey

```
1. User lands on app.opendata.london
         ↓
   Browse or search the catalog
   e.g. "air quality", "housing", "transport"
         ↓
   Dataset detail page shows:
     - Schema, update frequency, provider
     - Sample rows
     - Access methods: API / Snowflake / Download
         ↓
2. User creates org + project
         ↓
   Adds datasets to their Integration
   (subscribes to the datasets they want)
         ↓
3. User queries data:
   - REST API: POST /api/v1/query
   - Snowflake: OAuth connection, direct table access
   - Download: CSV export (future)
         ↓
4. Billing: metered by query volume / rows returned (Stripe)
```

---

## Platform — Built

### Auth & Organisations

| Feature | Where | Notes |
|---------|-------|-------|
| Email + password auth | `app/auth/routes.py` | Supabase GoTrue |
| OAuth login | `app/auth/routes.py` | Supabase OAuth providers |
| Password reset flow | `app/auth/routes.py` | Email via Resend |
| Session middleware | `app/auth/middleware.py` | `before()` hook, `get_user_id()` helper |
| Organisation create/list/switch | `app/orgs/routes.py` | Multi-org support |
| Project create/list/select | `app/projects/routes.py` | Projects scoped to orgs |
| Team members: invite, role change, remove | `app/team/routes.py` | Invite via Resend email |
| Invite accept/confirm flow | `app/team/invite.py` | Token-based invite links |
| Org settings: rename, avatar, transfer, delete | `app/settings/routes.py` | |
| SSO settings (UI shell) | `app/settings/routes.py` | Placeholder; not yet wired |

### Catalog

| Feature | Where | Notes |
|---------|-------|-------|
| Dataset definitions (seed) | `app/catalog/data.py` | ~10 seeded datasets: Companies House, TfL, Met Police, ONS, GLA, etc. |
| Catalog browse + search | `app/catalog/routes.py` | Keyword search + category filter |
| AI-powered search | `app/catalog/routes.py` | Anthropic API — natural language to dataset match |
| Dataset detail page | `app/pages/dataset.py` | Schema fields, sample rows, tags, update frequency |
| Favourites | `app/catalog/routes.py` | Star/unstar datasets per user |

### Integrations

| Feature | Where | Notes |
|---------|-------|-------|
| Create integration | `app/integrations/routes.py` | One integration per project |
| Toggle datasets in/out | `app/integrations/routes.py` | Subscribe / unsubscribe per dataset |
| Integration detail page | `app/pages/` | Shows active datasets + access credentials |

### API

| Endpoint | What it does |
|----------|-------------|
| `POST /api/v1/query` | Execute a SQL query against the user's subscribed datasets |

### Billing

| Feature | Where | Notes |
|---------|-------|-------|
| Stripe checkout | `app/billing/routes.py` | Subscription and one-off payment flows |
| Spend cap | `app/billing/routes.py` | Per-org query spend limit |
| Stripe webhook handler | `app/billing/stripe_webhook.py` | Isolated handler for Stripe events |
| Billing address | `app/billing/routes.py` | |

### Data Layer (odl-data)

**Medallion architecture:** raw → bronze (Python) → silver (dbt, typed) → gold (dbt, aggregates).

| Feature | Where | Notes |
|---------|-------|-------|
| Registry-driven ingestion | `contracts/source_registry.yml` + `sources/<id>/contract.yml` | Each source is a self-contained folder; registry is a lean enabled/disabled index |
| Raw zone | `raw/<source_id>/` | Immutable partitioned JSONL snapshots, one file per partition per run |
| Staging zone | `staging/<source_id>/` | Normalised Parquet (converted from raw JSONL) |
| Local warehouse | `warehouse/odl.duckdb` | DuckDB single-file warehouse; tables stored inside |
| dbt bronze models | `dbt/models/bronze/` | Passthrough from Python-loaded tables; adds dbt tests + docs |
| dbt silver models | `dbt/models/silver/` | Type casting, column renames, derived fields, null filtering |
| dbt macro | `dbt/macros/generate_schema_name.sql` | Overrides dbt default to use clean schema names (`bronze`, `silver`) not `main_bronze` |
| Export layer | `export/` | Snowflake-ready Parquet artifacts |
| Scheduler | `pipelines/scheduler.py` | Free local scheduler; cron-like intervals per source |
| Snowflake migration path | `pipelines/snowflake_trial.py` | Switch dbt profile; load `export/` via Snowflake stage |

**Active sources:**

| Source | Rows | Coverage | Refresh |
|--------|------|----------|---------|
| `london_air_quality` | ~500k | 60 sites, 8 pollutants, 90-day rolling | Hourly |
| `met_police_crime` | ~3.4M | 14 crime types, 33 boroughs, Feb 2023–Jan 2026 | Monthly |
| `land_registry_ppd` | ~4-5M (est.) | London property transactions, 1995–present | Monthly incremental |

### API Layer (odl-api)

FastAPI server running on Mac Mini, exposed to Vercel frontend via Cloudflare Tunnel. Auth via `X-API-Key` header validated against Supabase `integrations` table.

| Endpoint group | Endpoints | Notes |
|---------------|-----------|-------|
| Air Quality | `GET /v1/datasets/air-quality/sites` | 60 monitoring sites with metadata |
| | `GET /v1/datasets/air-quality/readings` | Filtered hourly readings (site, species, date, borough) |
| Crime | `GET /v1/datasets/crime/categories` | 14 crime type categories |
| | `GET /v1/datasets/crime/boroughs` | All boroughs |
| | `GET /v1/datasets/crime/incidents` | Filtered incidents (borough, type, month range, LSOA) |
| | `GET /v1/datasets/crime/summary` | Monthly counts by crime type |
| Property | `GET /v1/datasets/property/transactions` | Filtered PPD transactions (borough, postcode, type, tenure, price range, date) |
| | `GET /v1/datasets/property/summary` | Annual median/mean/count by borough + property type |

---

## Platform — Not Yet Built

| Feature | Notes |
|---------|-------|
| CSV / Parquet download endpoint | Let users download datasets directly |
| Snowflake OAuth wired end-to-end | UI shell exists; OAuth flow + table provisioning not complete |
| Usage dashboard | Query counts, rows returned, spend tracking per project |
| Dataset freshness indicators | Show last-updated timestamp live on catalog |
| Webhook notifications | Notify user when a subscribed dataset updates |
| Admin panel | Manage datasets, orgs, billing from internal tooling |

---

## Upcoming Feature: London Time-Series Streaming Layer

### Overview

OpenData.London already ingests London datasets in batch (air quality, housing, population). The next architectural step is to add a **streaming layer** — treating London's public data feeds as **event streams**, not just periodic snapshots.

The core idea: London's public datasets contain time-series data that changes continuously. Property prices, air quality readings, crime incidents, and transport disruptions are all, structurally, a sequence of events indexed by time. Modelling them as streams — rather than flat tables — unlocks multi-latency querying, real-time dashboards, and architecturally demonstrates the same patterns used in financial market data infrastructure.

This is not an academic exercise. The architecture mirrors what trading firms and systematic hedge funds operate at scale: a binary/structured event feed ingested in real-time, aggregated at multiple latency tiers (seconds, minutes, hours, days), with a queryable warehouse behind it. The difference is the domain: London civic data instead of order book ticks.

---

### Architecture

```
GLA / TfL / ONS / Met Police APIs (London Datastore, TfL Unified API, etc.)
       │
       │ ← source connectors (existing: london_datastore_api)
       │   (new: tfl_realtime, met_police_events, land_registry_feed)
       │
       ▼
  Stream Ingestor (new: pipelines/stream_ingestor.py)
       │  Polls or subscribes to source APIs at configurable intervals
       │  Each event written as a timestamped record to raw JSONL
       │
       ▼
  Raw Zone (existing: raw/<source_id>/<timestamp>.jsonl)
       │  Immutable append-only event log
       │  Each record: { event_id, source_id, occurred_at, payload }
       │
       ├──► Real-time tier (new: pipelines/stream_aggregator.py)
       │        Maintains in-memory rolling window (last 60s)
       │        Writes 1-minute snapshots to Redis or DuckDB in-memory table
       │        Queryable via: GET /api/v1/stream/{source_id}/live
       │
       ├──► Hourly tier (dbt model: models/silver/hourly_<source>.sql)
       │        dbt incremental model; aggregates raw events by hour
       │        Stored in DuckDB warehouse as silver table
       │        Queryable via: POST /api/v1/query (SQL)
       │
       └──► Daily tier (dbt model: models/gold/daily_<source>.sql)
                dbt model; full-day summary, Snowflake-ready
                Written to export/ as Parquet
                Queryable via: Snowflake stage or POST /api/v1/query
```

**Key principle:** the same raw event log feeds all three latency tiers. Real-time aggregation runs in-process; hourly and daily tiers run via dbt on a schedule. No data is duplicated — only the aggregation window changes.

---

### Three-Tier Latency Model

| Tier | Latency | Storage | Query path | Use case |
|------|---------|---------|------------|----------|
| Real-time | < 60s | In-memory / Redis | REST stream endpoint | Live dashboard, anomaly detection |
| Hourly | < 1h | DuckDB silver table | SQL via `/api/v1/query` | Trend analysis, alerts |
| Daily | < 24h | DuckDB gold / Parquet export | SQL or Snowflake | Reporting, ML feature store |

This is structurally identical to how a market data platform handles tick data: the same event stream is consumed at different granularities for different consumer needs.

---

### Target Data Sources

#### 1. TfL Real-Time (highest value, lowest latency)

TfL's Unified API is free, open, and already returns structured JSON. It provides:

- **Line statuses** — tube/bus/overground disruptions, updated every ~30s
- **Arrivals** — predicted arrival times per stop, updated every ~30s
- **Crowding** — station-level crowding scores

Treating line status changes as an **event stream** (e.g. `{ line: "central", status: "Minor Delays", occurred_at: ... }`) produces a tick-level feed of London transport state. The "order book" equivalent is the real-time disruption state across all lines.

```
New TfL connector in source_registry.yml:
  source_id: tfl_line_status
  connector: tfl_unified_api
  endpoint: /Line/Mode/tube,overground,dlr,elizabeth-line/Status
  schedule_interval_seconds: 30
  stream_mode: true
```

#### 2. London Air Quality Network (LAQN)

King's College London operates the [LAQN API](https://www.londonair.org.uk/LondonAir/API/) — free, no auth, returns hourly sensor readings for ~150 monitoring stations across London. Pollutants: NO2, PM2.5, PM10, O3.

This is already in the ODL data source registry (`london_air_quality`). The upgrade is to treat each sensor reading as a **timestamped event** rather than a batch snapshot:

```
{ station_id: "MY1", pollutant: "NO2", value: 42.1, unit: "ug/m3", occurred_at: "2026-03-30T14:00:00Z" }
```

With 150 stations × hourly readings × 4 pollutants = ~600 events/hour. Aggregated at the silver layer into hourly borough-level averages; at the gold layer into daily summaries with trend indicators.

#### 3. Land Registry Price Paid Data ✅ Built

The Land Registry publishes [monthly Price Paid Data](https://www.gov.uk/government/collections/price-paid-data) as a free CSV download. Each transaction is a financial event:

```
{ transaction_id, price, date_of_transfer, postcode, property_type, tenure, ... }
```

**Status:** connector built (`sources/land_registry_ppd/`). Streams yearly CSVs 1995–present filtered to GREATER LONDON. Silver layer: price as integer, decoded property_type/tenure/new_build, borough with consistent casing. API: `GET /v1/datasets/property/transactions` and `/summary`.

The streaming interpretation: each new month's file is a batch of events. The gold layer will produce median price trajectories by borough, property type, and tenure — a financial time series directly analogous to OHLCV candlestick data.

#### 4. Met Police Crime Data ✅ Built

The [data.police.uk API](https://data.police.uk/docs/) is free and open. Street-level crime incidents by location and month.

```
{ category, location: { lat, lng, street }, outcome, month }
```

**Status:** connector built (`sources/met_police_crime/`). Downloads 36 months via HTTP range requests against the cumulative national archive (pulls only Met Police CSV ~3.8MB/month from 1.7GB ZIP). 3.4M rows. Silver layer: typed coordinates, borough extracted from LSOA name. API: 4 endpoints including `/summary` for monthly counts by type.

---

### New Files (proposed)

| File | Status | What it does |
|------|--------|-------------|
| `sources/london_air_quality/connector.py` | ✅ Built | LAQN air quality connector: per-station hourly readings |
| `sources/met_police_crime/connector.py` | ✅ Built | Met Police bulk archive via HTTP range requests |
| `sources/land_registry_ppd/connector.py` | ✅ Built | Land Registry Price Paid connector: yearly CSVs 1995–present |
| `pipelines/stream_ingestor.py` | Planned | Poll-based stream ingestor: fetches source at interval, appends new events to raw JSONL with deduplication on `event_id` |
| `pipelines/stream_aggregator.py` | Planned | In-memory aggregator: maintains rolling 60s window per source |
| `pipelines/connectors/tfl_unified.py` | Planned | TfL Unified API connector: `/Line/.../Status`, arrivals, crowding |
| `dbt/models/silver/hourly_tfl_disruptions.sql` | Planned | Hourly disruption duration per line (incremental) |
| `dbt/models/gold/daily_property_prices.sql` | Planned | Daily median price per borough × property type |
| `app/api_v1/stream_routes.py` | Planned | `GET /api/v1/stream/{source_id}/live` — returns current in-memory snapshot |

---

### Why This Matters for the Portfolio

The three-tier model (real-time / hourly / daily) answers the exact question asked in HFT/quant infrastructure interviews:

> *"You have data in Frankfurt. London needs it for a real-time report, an hourly report, and a daily report. How do you architect that?"*

The answer is already implemented here — with London civic data instead of market ticks. The transport layer (TfL status events) demonstrates sub-minute streaming; the air quality layer demonstrates sensor event aggregation; the property price layer demonstrates batch-to-stream conversion of financial data.

The portfolio narrative becomes: **"I built a multi-latency streaming platform over London's public data infrastructure — architecturally equivalent to a market data feed, applied to civic intelligence."**

---

## Upcoming Feature: Live Data Dashboard (Public Landing Page)

### Overview

The current entry point (`/catalog`) is functional but static. The opportunity is to add a **live data strip or grid at the top of the public landing page** — visible before login — that demonstrates the platform's real-time capabilities immediately, to any visitor.

The goal is a Bloomberg-terminal-aesthetic ticker row or card grid: dark background, monospace numbers, subtle green/red deltas, auto-refreshing every 30–60 seconds via HTMX polling (`hx-trigger="every 30s"`). No WebSockets required — HTMX's `hx-get` + `hx-swap` is sufficient for this refresh rate and has zero infrastructure overhead.

**Design principle:** each widget is a self-contained `<div>` that polls its own backend endpoint. The backend endpoint calls the upstream API, formats the value, and returns a pre-rendered HTML fragment. HTMX swaps it in-place. No JavaScript state, no client-side fetch, no JSON parsing in the browser.

```
GET /live/boe-rate          → returns <span>3.75%</span> + delta badge
GET /live/tfl-status        → returns mini disruption list
GET /live/air-quality       → returns top-3 worst stations
GET /live/companies-events  → returns last 5 CH stream events
GET /live/gilt-yield        → returns current 10Y gilt yield
```

All endpoints are thin: call upstream → format → return HTML fragment. Cacheable for 30s server-side to avoid hammering upstream APIs.

---

### Widget Catalogue

#### 1. Bank of England Base Rate

**Source:** [Bank of England Interactive Database](https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp) — free, no auth, CSV endpoint.

**Endpoint:** `https://www.bankofengland.co.uk/boeapps/database/_iadb-FromShowColumns.asp?csv.x=yes&SeriesCodes=IUMABEDR`

**Refresh:** daily (rate only changes on MPC meeting days ~8x/year, but the widget confirms the current value)

**Widget:**
```
┌─────────────────────────────────┐
│  BOE BASE RATE          DAILY   │
│  3.75%                          │
│  ↓ –0.25pp since Feb 2026       │
└─────────────────────────────────┘
```

Why it's interesting: Bank Rate is the single most important number in UK finance. Every mortgage, every gilt yield, every credit spread is priced off it. Showing it live — even if it only changes 8 times a year — signals that the platform tracks the authoritative source.

---

#### 2. UK 10-Year Gilt Yield

**Source:** [Bank of England yield curves](https://www.bankofengland.co.uk/statistics/yield-curves) — daily nominal spot curve, free CSV download.

**Endpoint:** BoE IADB CSV for series `IUDMNPY` (10Y nominal spot gilt yield)

**Refresh:** daily (published by ~5pm each business day)

**Widget:**
```
┌─────────────────────────────────┐
│  10Y GILT YIELD         DAILY   │
│  4.62%                          │
│  ↑ +0.08pp today                │
└─────────────────────────────────┘
```

Why it's interesting for a quant audience: gilt yields are a fundamental risk-free rate benchmark. Displaying it alongside the base rate immediately frames the platform as financially literate — you're showing the spread between policy rate and market rate, implicitly. Any hedge fund person reading this page will notice.

---

#### 3. FTSE 100 / FTSE 250

**Source:** [Alpha Vantage](https://www.alphavantage.co/) (free tier, 25 calls/day) or [Finnhub](https://finnhub.io/) (free tier, 60 calls/minute). Both provide `^FTSE` (FTSE 100) and `^FTMC` (FTSE 250) as quote symbols.

**Alternative (zero-API-key):** `https://query1.finance.yahoo.com/v8/finance/chart/^FTSE` — Yahoo Finance's undocumented but widely-used public endpoint. No auth, returns JSON with current price and previous close.

**Refresh:** every 60s during market hours (08:00–16:30 London time), frozen outside hours

**Widget:**
```
┌─────────────────────────────────┐
│  FTSE 100             LIVE      │
│  8,423.17   ▲ +0.42%            │
│  FTSE 250   6,201.44  ▼ –0.18% │
└─────────────────────────────────┘
```

Why it matters: FTSE 100 is the most-watched UK financial number. Having it tick live on a London data platform is immediately credible to any finance-adjacent visitor. The FTSE 250 (more UK-domestic exposure) adds depth.

---

#### 4. GBP/USD and GBP/EUR Exchange Rates

**Source:** [Frankfurter API](https://www.frankfurter.app/) — completely free, no key, no rate limits, ECB data.

**Endpoint:** `https://api.frankfurter.app/latest?from=GBP&to=USD,EUR`

**Refresh:** every 60s (ECB rates update ~4pm Frankfurt time on business days; the API returns latest available)

**Widget:**
```
┌─────────────────────────────────┐
│  GBP/USD              LIVE      │
│  1.2947   ↑ +0.003 today        │
│  GBP/EUR  1.1834   ↓ –0.001     │
└─────────────────────────────────┘
```

Why it fits: Sterling rates are the heartbeat of London finance. Rothschild, every hedge fund, every UK bank watches GBP/USD. This is a zero-cost, zero-auth signal that any Londoner immediately understands.

---

#### 5. TfL Network Status

**Source:** [TfL Unified API](https://api.tfl.gov.uk/) — free, requires registration for API key (takes 2 minutes, no billing).

**Endpoint:** `https://api.tfl.gov.uk/Line/Mode/tube,elizabeth-line,overground,dlr/Status?app_key=...`

**Refresh:** every 30s

**Widget:**
```
┌─────────────────────────────────┐
│  LONDON TRANSPORT       LIVE    │
│  ● Central         Good service │
│  ⚠ Jubilee    Minor Delays      │
│  ● Elizabeth line  Good service │
│  ✕ Northern    Part suspended   │
└─────────────────────────────────┘
```

Why it works: TfL status is something every Londoner checks daily. It's instantly relatable, confirms the platform is London-specific, and demonstrates real-time data ingestion from a live API in a way anyone can verify by opening their phone.

---

#### 6. Companies House — Live Filing Events

**Source:** [Companies House Streaming API](https://developer-specs.company-information.service.gov.uk/streaming-api/guides/overview) — already consumed by Alliela. This widget reads from your own `ch.raw_events` Postgres table (already populated) rather than hitting CH directly.

**Backend:** `SELECT company_name, event_type, occurred_at FROM ch.raw_events ORDER BY occurred_at DESC LIMIT 5`

**Refresh:** every 10s

**Widget:**
```
┌──────────────────────────────────────────┐
│  UK COMPANY EVENTS              LIVE     │
│  ACME VENTURES LTD    new-filing  2s ago │
│  SMITH & CO LTD       officer     8s ago │
│  GREENFIELD LABS      dissolution 14s ago│
│  MERIDIAN CAPITAL     new-filing  21s ago│
│  HARTLEY GROUP PLC    psc-change  33s ago│
└──────────────────────────────────────────┘
```

Why it's powerful: this is the only widget where the data comes from *your own pipeline*, not a third-party API. It proves the stream worker is running live. To a technical recruiter or engineer visiting the site, seeing real-time company filing events is a clear signal that there's a real infrastructure stack behind the platform — not just a front-end.

---

#### 7. London Air Quality Index

**Source:** [LAQN API](https://www.londonair.org.uk/LondonAir/API/) — completely free, no auth.

**Endpoint:** `https://api.erg.ic.ac.uk/AirQuality/Hourly/MonitoringIndex/GroupName=London/Json`

**Refresh:** every 60 minutes (LAQN updates hourly)

**Widget:**
```
┌─────────────────────────────────────┐
│  LONDON AIR QUALITY    HOURLY       │
│  Marylebone Rd   NO2: 67  MODERATE  │
│  Heathrow        PM2.5: 18   LOW    │
│  City of London  NO2: 44     LOW    │
│  Updated: 14:00 today               │
└─────────────────────────────────────┘
```

Why it's interesting as a non-financial widget: air quality is a GLA policy priority, it's health-relevant to every Londoner, and it demonstrates sensor-level time-series data ingestion. It also visually differentiates the platform — not everything is financial, which is a strength (broad London data platform, not just a finance feed).

---

#### 8. UK CPI Inflation (Latest Print)

**Source:** [ONS API](https://api.beta.ons.gov.uk/v1) — fully open, free, no auth required.

**Endpoint:** `https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions/latest/observations?time=*&aggregate=cpih1dim1A0&geography=K02000001`

**Refresh:** monthly (ONS releases CPI on a fixed schedule; widget shows latest print + date)

**Widget:**
```
┌─────────────────────────────────┐
│  UK CPI INFLATION    MONTHLY    │
│  3.4%   (Feb 2026)              │
│  Core CPI: 3.1%                 │
│  Next release: 16 Apr 2026      │
└─────────────────────────────────┘
```

Why it belongs: CPI is the BoE's primary mandate target. Pairing it with the Base Rate widget (widget 1) creates an implicit narrative: policy rate is 3.75%, inflation is 3.4%, real rate is +0.35%. Any macro-aware visitor reads this instantly. It's also free, authoritative (ONS is the UK's national statistics body), and changes infrequently enough that the widget is always "fresh" without any infrastructure burden.

---

### Layout Options

**Option A — Ticker strip (minimal):**
A single horizontal row of values across the top of the catalog page, styled like a financial terminal ticker. Updates in-place via HTMX. Compact, low-distraction, professional.

```
BOE RATE 3.75%  |  10Y GILT 4.62%  |  FTSE 100 ▲8,423  |  GBP/USD 1.2947  |  TfL ⚠ 2 disruptions  |  CPI 3.4%
```

**Option B — Dashboard card grid (full featured):**
A 4-column grid of cards before the catalog entries. Each card has its own HTMX poll interval. Suitable for a dedicated `/dashboard` or `/live` page rather than inserting into the catalog.

**Option C — Hybrid:**
Ticker strip always visible at the top of the catalog. Clicking any item expands an inline detail card (HTMX `hx-swap="outerHTML"`). No page navigation required.

**Recommended:** Option C. The ticker strip is low-footprint and always visible; the expand-on-click makes deeper detail available without cluttering the catalog browsing experience.

---

### Implementation Notes

All widgets use HTMX polling — no JavaScript required:

```html
<!-- Example: BoE Rate widget fragment target -->
<div id="boe-rate-widget"
     hx-get="/live/boe-rate"
     hx-trigger="load, every 60s"
     hx-swap="innerHTML">
  <span class="stat-value">—</span>
</div>
```

Each `/live/*` route:
1. Checks an in-process cache (TTL matches widget refresh interval)
2. On cache miss: calls upstream API, parses response, formats HTML fragment
3. Returns the fragment directly (no JSON, no client-side rendering)

This pattern is already consistent with how the rest of the app works (FastHTML, server-rendered fragments, HTMX swaps). No new frontend dependencies.

**Rate limit summary for free tiers:**

| Widget | Source | Rate limit | Notes |
|--------|--------|------------|-------|
| BoE Base Rate | Bank of England IADB | None documented | Cache for 1h |
| 10Y Gilt Yield | Bank of England IADB | None documented | Cache for 1h |
| FTSE 100/250 | Yahoo Finance (unofficial) | Soft limit ~2000/day | Cache for 60s |
| GBP/USD, GBP/EUR | Frankfurter API | None | Cache for 60s |
| TfL Status | TfL Unified API | 500 req/min (free key) | Cache for 30s |
| Companies Events | Own Postgres (ch.raw_events) | None — own DB | Cache for 10s |
| Air Quality | LAQN / ERG API | None documented | Cache for 1h |
| UK CPI | ONS Beta API | None documented | Cache for 24h |

That is original, technically credible, and directly relevant to both Rothschild (financial data) and systematic hedge funds (data infrastructure at scale).

---

## Upcoming Feature: Real Estate Intelligence Module

### Why Real Estate

UK residential and commercial property is a £8+ trillion asset class. It is also one of the most data-rich, publicly documented markets in the world — the UK government mandates disclosure at every stage: sale registration, energy performance, planning permission, title ownership. Almost all of it is free and open under the Open Government Licence.

The opportunity for OpenData.London is to aggregate these fragmented official sources into a unified intelligence layer — and then surface it as live widgets, queryable datasets, and alerts. The target audience is broad: property investors, mortgage brokers, PropTech developers, estate agents, urban planners, housing researchers, and banks with UK real estate exposure (including Rothschild's advisory and financing arms).

Unlike Rightmove or Zoopla (listings-only, walled gardens), ODL's value proposition is **transactional + structural intelligence**: what actually sold, for what, with what energy rating, next to what planning applications, owned by whom.

---

### Data Sources

#### 1. HM Land Registry — Price Paid Data (PPD)

**Source:** [HM Land Registry Price Paid Data](https://www.gov.uk/government/collections/price-paid-data) — free, Open Government Licence, no auth required.

**What it contains:** Every residential property transaction in England and Wales since January 1995. 24+ million records. Fields: price, date of transfer, postcode, property type (detached/semi/terraced/flat), new build flag, estate type (freehold/leasehold), address.

**Access:** Monthly CSV bulk download + SPARQL endpoint for programmatic queries.

**Endpoint (CSV):**
```
http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv
```
Updated monthly. Last updated: February 2026 data added 27 March 2026.

**Intelligence value:** The most authoritative transaction record in the UK. No estimates — actual registered sale prices. The foundation of every serious UK property analysis.

---

#### 2. UK House Price Index (UKHPI)

**Source:** [HM Land Registry / ONS UKHPI](https://landregistry.data.gov.uk/app/ukhpi/) — free, Open Government Licence, queryable API.

**What it contains:** Monthly indexed house prices by region, local authority, property type, buyer type (first-time buyer / former owner occupier). Covers England, Wales, Scotland, Northern Ireland. Average UK house price: £268,421 (January 2026, +1.3% YoY).

**API:**
```
https://landregistry.data.gov.uk/app/ukhpi/browse?location=http%3A%2F%2Flandregistry.data.gov.uk%2Fid%2Fregion%2Flondon&from=2020-01&to=2026-01&lang=en
```
Also queryable via SPARQL. JSON and CSV output. No auth.

**Intelligence value:** Enables time-series charting of price trends by London borough — the "OHLCV candlestick" equivalent for UK residential property. Monthly granularity going back to 1995.

---

#### 3. Energy Performance Certificates (EPC)

**Source:** [MHCLG EPC Open Data Portal](https://epc.opendatacommunities.org/) — free, requires registration (email only, no billing).

**What it contains:** ~30 million EPC certificates for domestic buildings in England and Wales. Fields: address, postcode, current and potential energy rating (A–G), floor area, property type, construction year, heating type, CO2 emissions, estimated fuel cost.

**API:**
```
https://epc.opendatacommunities.org/api/v1/domestic/search?postcode=EC1A1BB&size=25
```
REST API with JSON output. Bearer token auth (free registration).

**Intelligence value:** Every property's energy efficiency rating is now financially material — EPC ratings affect mortgage eligibility (lenders increasingly refusing sub-D), rental legality (minimum E for lettings), and retrofit costs. Joining EPC data to PPD transactions gives you: *did this property sell at a discount because of its EPC rating?* That is a genuine analytical product.

---

#### 4. Planning Applications — planning.data.gov.uk

**Source:** [MHCLG Planning Data Platform](https://www.planning.data.gov.uk/) — free, Open Government Licence, REST API, no auth.

**What it contains:** National dataset of planning applications from 425+ local planning authorities in England. Fields: reference, description, decision, decision date, appeal status, site address, coordinates, UPRN.

**API:**
```
https://www.planning.data.gov.uk/api/v1/entity.json?dataset=planning-application&geometry_relation=intersects&geometry=...
```
GeoJSON-compatible. Queryable by geography, date, decision type.

**Intelligence value:** Planning applications are a leading indicator of property activity. A planning permission granted in a postcode signals incoming development, densification, or infrastructure change — all of which affect prices. This is the data that PropTech and hedge fund real estate desks pay for. Here it's free.

---

#### 5. HM Land Registry — UK Land Ownership (INSPIRE / Title Register)

**Source:** [Use Land and Property Data service](https://use-land-property-data.service.gov.uk/) — free tier available for non-commercial use, API key required (free registration).

**What it contains:** INSPIRE Index Polygons (the spatial footprint of every registered title in England and Wales), overseas company ownership of UK land, corporate ownership data.

**Intelligence value:** The "who owns what" layer. Combined with Companies House (which ODL/Alliela already has), this creates a corporate → land ownership graph: *which UK properties are owned by companies whose directors are in your graph?* That is a unique product no public tool currently offers.

---

#### 6. ONS Sub-regional House Price Statistics

**Source:** [ONS](https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/ukhousepriceindexmonthlypricestatistics) — free, no auth, CSV + API.

**What it contains:** Mean and median prices, transaction volumes, and 12-month price change by local authority, region, and country. Updated monthly.

**Intelligence value:** Borough-level price velocity — which London boroughs are accelerating vs decelerating. Combined with planning application volume, this gives a forward-looking signal: high planning activity + rising prices = developer pressure zone.

---

### Intelligence Products (What to Build)

These are the analytical outputs — the "tools" — built by combining the sources above.

---

#### Tool 1: London Borough Price Heatmap (Live Widget)

**Inputs:** UKHPI monthly by local authority + ONS sub-regional stats

**Output:** An SVG or canvas map of London boroughs colour-coded by 12-month price change. Green = rising above London average, red = falling. Updated monthly when new UKHPI data drops.

**Widget format:**
```
┌──────────────────────────────────────────┐
│  LONDON PROPERTY PRICES     JAN 2026     │
│  [borough map — colour gradient]         │
│  Hackney     +4.2%   Croydon   +1.1%     │
│  Kensington  –0.8%   Barking   +3.7%     │
│  City of Lon +0.3%   Avg: +1.3% YoY      │
└──────────────────────────────────────────┘
```

**Route:** `GET /live/property-heatmap` — returns pre-rendered SVG fragment, HTMX-swapped, refreshes daily.

---

#### Tool 2: Transaction Velocity Monitor

**Inputs:** HM Land Registry PPD (monthly CSV) — transaction counts by postcode district

**Output:** A ranked table of London postcode districts by transaction volume in the last 30/90/180 days, with MoM and YoY change. Effectively a "liquidity" signal for the London property market.

**Why it matters:** Low transaction volume in a previously active district often precedes price correction (sellers holding, buyers withdrawing). High volume + rising price = strong demand signal. Hedge fund real estate desks track this manually. ODL can automate it.

**dbt model:** `models/gold/transaction_velocity_by_postcode.sql` — incremental, partitioned by month.

---

#### Tool 3: EPC × Price Correlation ("Green Discount / Premium")

**Inputs:** PPD (price + address) joined to EPC (rating + floor area) via UPRN or address matching

**Output:** For each London borough and property type: median price per sq metre by EPC band (A–G). Answer the question: *how much more does an EPC A flat sell for vs an EPC D flat of the same size in the same borough?*

**Why it matters:** This is a financially material question for anyone buying, lending against, or insuring UK property. The gap is widening as minimum EPC standards tighten. This product exists nowhere for free.

**Complexity note:** UPRN matching is reliable for ~80% of records. Address fuzzy matching handles the rest. This is a dbt + DuckDB transform problem.

---

#### Tool 4: Planning Pressure Index

**Inputs:** planning.data.gov.uk (application counts by geography + decision) + UKHPI (price change)

**Output:** For each London borough: planning application volume in last 12 months (by type: residential, commercial, permitted development), approval rate, and overlay with price trend. Boroughs with high application volume + high approval rate = supply pressure zone.

**Live widget version:**
```
┌──────────────────────────────────────────────┐
│  PLANNING PRESSURE INDEX         THIS MONTH  │
│  Tower Hamlets   ████████░░  312 apps  HIGH  │
│  Southwark       ██████░░░░  241 apps  MED   │
│  Westminster     █████░░░░░  198 apps  MED   │
│  Hackney         ████░░░░░░  167 apps  LOW   │
└──────────────────────────────────────────────┘
```

---

#### Tool 5: Corporate Land Ownership Lookup

**Inputs:** HM Land Registry overseas/corporate ownership data + Companies House graph (Alliela)

**Output:** Given a company name or number, show all UK properties registered in that company's name — with title polygon on a map, acquisition date, and estimated current value (from UKHPI index applied to PPD purchase price).

**Why it's unique:** This joins two datasets that are both public but never combined in a user-facing tool. Every AML team, investigative journalist, and property researcher wants this. The data is free. The join is the product.

**Route:** `GET /intelligence/corporate-ownership/{company_number}` — calls Land Registry title data + queries Alliela's CH graph + returns GeoJSON + property table.

---

#### Tool 6: Mortgage Stress Indicator

**Inputs:** BoE base rate history (already in live widget) + UKHPI regional prices + ONS regional earnings data

**Output:** For each London borough: estimated mortgage affordability ratio (median house price / median annual earnings), current monthly payment on a 75% LTV repayment mortgage at current BoE rate, and change vs 12 months ago.

**Why it matters:** At 3.75% base rate with London prices, affordability is stretched. This widget makes that concrete and borough-specific. Any bank, mortgage broker, or housing policy researcher needs it. No free tool currently shows it at borough granularity.

```
┌──────────────────────────────────────────────────┐
│  MORTGAGE AFFORDABILITY      LONDON, JAN 2026    │
│  Median price:        £521,000                   │
│  75% LTV mortgage:    £390,750                   │
│  At 3.75% + spread:   ~5.5% rate                 │
│  Monthly payment:     ~£2,340                    │
│  Price/earnings ratio: 11.2x  (London avg)       │
│  vs 12mo ago:  ▲ +0.4x  (rate rise effect)       │
└──────────────────────────────────────────────────┘
```

---

#### Tool 7: New Build vs Resale Price Premium Tracker

**Inputs:** PPD (new build flag field) — filter by `new_build = Y` vs `N`, same postcode, same property type, same quarter

**Output:** For each London borough, what premium (or discount) do new builds command vs resale properties of the same type. Updated monthly.

**Why it matters:** New build premium is a key metric for developers (pricing), buyers (overpaying?), and mortgage lenders (valuation risk on day-one decline). This requires no additional data source — it's all inside PPD, just never surfaced cleanly.

---

### Data Pipeline Architecture for Real Estate

```
HM Land Registry PPD (monthly CSV)
       │
       ▼
pipelines/connectors/land_registry_ppd.py
  → downloads monthly update CSV
  → appends to raw/land_registry_ppd/<year_month>.jsonl
       │
       ▼
dbt/models/bronze/land_registry_ppd.sql       ← parse + type CSV
dbt/models/silver/ppd_london.sql              ← filter to London postcodes
dbt/models/silver/ppd_monthly_volume.sql      ← transaction counts by postcode/month
dbt/models/gold/transaction_velocity.sql      ← velocity + MoM/YoY deltas
dbt/models/gold/new_build_premium.sql         ← new build vs resale by borough

EPC API (on-demand REST)
       │
       ▼
pipelines/connectors/epc_api.py
  → queries by postcode batch
  → raw/epc/<postcode_district>.jsonl
       │
       ▼
dbt/models/bronze/epc_certificates.sql
dbt/models/gold/epc_price_correlation.sql     ← JOIN to PPD via UPRN/address

UKHPI (monthly CSV/API)
       │
       ▼
pipelines/connectors/ukhpi.py
dbt/models/silver/ukhpi_london_boroughs.sql
dbt/models/gold/borough_price_heatmap.sql     ← feeds live widget

planning.data.gov.uk (REST API)
       │
       ▼
pipelines/connectors/planning_data.py
dbt/models/silver/planning_applications_london.sql
dbt/models/gold/planning_pressure_index.sql   ← feeds live widget
```

---

### New API Routes (proposed)

| Route | Returns | Refresh |
|-------|---------|---------|
| `GET /live/property-prices` | Borough heatmap fragment | Monthly |
| `GET /live/planning-pressure` | Top 5 boroughs by application volume | Monthly |
| `GET /live/mortgage-affordability` | London affordability widget | Monthly |
| `GET /intelligence/borough/{slug}` | Full borough profile: prices, EPCs, planning, velocity | On request |
| `GET /intelligence/postcode/{pc}` | Postcode drill-down: recent sales, EPC ratings, nearby planning apps | On request |
| `GET /intelligence/corporate-ownership/{number}` | CH company → Land Registry titles | On request |

---

### Source Summary

| Dataset | Provider | Licence | Auth | Update frequency |
|---------|----------|---------|------|-----------------|
| [Price Paid Data](https://www.gov.uk/government/collections/price-paid-data) | HM Land Registry | OGL | None | Monthly |
| [UK House Price Index](https://landregistry.data.gov.uk/app/ukhpi/) | HMLR + ONS | OGL | None | Monthly |
| [EPC Certificates](https://epc.opendatacommunities.org/) | MHCLG | OGL* | Free registration | Monthly |
| [Planning Applications](https://www.planning.data.gov.uk/) | MHCLG | OGL | None | Continuous |
| [Land Ownership / INSPIRE](https://use-land-property-data.service.gov.uk/) | HM Land Registry | OGL* | Free API key | Monthly |
| [ONS Sub-regional HPI](https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/ukhousepriceindexmonthlypricestatistics) | ONS | OGL | None | Monthly |

*OGL with registration requirement for bulk/API access.
