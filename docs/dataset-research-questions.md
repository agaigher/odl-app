# Dataset Research Questions — OpenData.London

These questions need to be answered before we can fully design ingestion pipelines and access tiers for each dataset. Please research each one and fill in the answers.

---

## General questions (apply to all datasets)

1. Is the dataset fully open / public, or does access require registration, an API key, or a data sharing agreement?
2. What is the official update frequency (hourly, daily, monthly, ad-hoc)?
3. What is the approximate total row count / file size of the full dataset?
4. Is there a public API (REST, OData, SPARQL)? If so, does it support pagination and filtering?
5. Is bulk download available (CSV, Parquet, Shapefile)?
6. Are there any usage restrictions, attribution requirements, or licence conditions (OGL, OS OpenData, commercial restrictions)?
7. What is the natural partition key for ML / parallel processing? (e.g. date, borough, category)
8. Is there a changelog or version history so we can do incremental ingestion rather than full reloads?

---

## Dataset-specific questions

### 1. UK Companies House (Live)
- Source: https://www.gov.uk/government/organisations/companies-house
- Does the bulk data product include live company status or is it a monthly snapshot?
- Is the streaming API (Companies House Streaming API) free or paid?
- What volume of updates per day on average?
- Primary key: company number — is this stable across updates?

### 2. TfL Transport Network & Telemetry
- Source: https://api.tfl.gov.uk
- Which feeds are truly real-time vs scheduled? (bus arrivals, tube status, bike points, road disruptions)
- Is the Unified API free with registration?
- What rate limits apply?
- For historical data (e.g. journey times) — how far back does it go and in what format?

### 3. London Planning Applications & Real Estate
- Source: 32 London boroughs — is there a unified feed or does each borough publish separately?
- Does the Planning London Datahub (https://www.london.gov.uk/programmes-strategies/planning/planning-data-and-research/planning-london-datahub) cover all 32 boroughs?
- Update frequency per borough?
- Is there a consistent schema across boroughs or do we need to normalise?

### 4. FCA Regulatory Register
- Source: https://register.fca.org.uk
- Is there a bulk download or only the search API?
- Update frequency for firm status changes?
- Any restrictions on commercial redistribution?

### 5. HM Land Registry — Title & Price Paid
- Source: https://www.gov.uk/government/collections/price-paid-data
- Price Paid Data is OGL — confirmed open for commercial use?
- Full dataset is ~25M rows — is the monthly update an incremental diff or full reload?
- Does the Title Register (ownership) require a separate agreement?
- Natural partition: transaction date + property type?

### 6. Metropolitan Police Crime Data
- Source: https://data.police.uk
- Bulk download is available monthly — is there an API for filtered queries too?
- Lat/lon is included but snapped to street level — is this suitable for borough-level partitioning?
- How far back does historical data go?

### 7. London Air Quality Network
- Source: https://www.londonair.org.uk / https://data.london.gov.uk
- Hourly readings per monitoring site — how many active sites?
- Is there a REST API for live readings?
- Full history available or rolling window only?

### 8. Electoral Register & Demographics
- Source: ONS / GLA
- Is the electoral register publicly available at individual level or only aggregate?
- Which specific ONS datasets cover London demographics (mid-year estimates, Census 2021)?
- Update schedule for Census-derived data?

---

## Access tier questions (for product design)

1. For each dataset: would a typical customer want the full history or just recent N months?
2. Which datasets are likely to be queried at high frequency (> 100 requests/day per customer)?
3. Are there any datasets where the original source already provides a good enough free API — i.e. where our value-add is normalisation and consistency rather than access?
4. Which datasets would benefit most from pre-built aggregations (e.g. monthly borough summaries) vs raw row access only?
