"""
London Database — catalog definitions.

To add a new dataset: append a dict to DATASETS and redeploy.
seed_catalog() upserts all definitions into Supabase on startup.
"""
import httpx
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

DATASETS = [
    {
        "slug": "uk-companies-house",
        "title": "UK Companies House (Live)",
        "description": "Continuously updated registry of all UK corporate entities, directors, and filings. Synchronised sub-second.",
        "long_description": (
            "The Companies House dataset provides a complete, continuously-updated view of every "
            "corporate entity registered in the United Kingdom. This includes active companies, "
            "dissolved entities, LLPs, and overseas companies. Director and officer appointments, "
            "PSC (persons with significant control) records, and all statutory filings are included "
            "and kept in sync sub-second with the Companies House streaming API. "
            "This dataset is essential for KYC/AML pipelines, supplier due diligence, credit risk, "
            "and corporate intelligence workflows."
        ),
        "category": "Corporate Registries",
        "provider": "Companies House",
        "update_frequency": "Real-time",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["corporate", "kyc", "aml", "directors", "filings", "compliance", "uk"],
        "schema_fields": [
            {"name": "company_number", "type": "text", "description": "Unique Companies House identifier"},
            {"name": "company_name", "type": "text", "description": "Registered company name"},
            {"name": "company_status", "type": "text", "description": "Active, Dissolved, Liquidation, etc."},
            {"name": "company_type", "type": "text", "description": "ltd, plc, llp, etc."},
            {"name": "incorporation_date", "type": "date", "description": "Date of incorporation"},
            {"name": "registered_office", "type": "jsonb", "description": "Full registered address object"},
            {"name": "sic_codes", "type": "text[]", "description": "Standard Industry Classification codes"},
            {"name": "officers", "type": "jsonb", "description": "Array of current director/officer records"},
            {"name": "pscs", "type": "jsonb", "description": "Persons with significant control"},
            {"name": "last_accounts_date", "type": "date", "description": "Date of most recent filed accounts"},
            {"name": "updated_at", "type": "timestamptz", "description": "Last sync timestamp"},
        ],
        "sample_rows": [
            {"company_number": "00000006", "company_name": "MARINE AND GENERAL MUTUAL LIFE ASSURANCE SOCIETY", "company_status": "Active", "company_type": "private-unlimited-nsc", "incorporation_date": "1884-01-01"},
            {"company_number": "00000010", "company_name": "DŴR CYMRU CYFYNGEDIG", "company_status": "Active", "company_type": "private-limited-guarant-nsc-limited-exemption", "incorporation_date": "1989-03-17"},
            {"company_number": "00000050", "company_name": "THE FOOTBALL ASSOCIATION LIMITED", "company_status": "Active", "company_type": "private-limited-guarant-nsc", "incorporation_date": "1948-05-24"},
        ],
    },
    {
        "slug": "tfl-transport-network",
        "title": "TfL Transport Network & Telemetry",
        "description": "Live feeds of London Underground, buses, Overground, and road traffic incidents.",
        "long_description": (
            "A unified stream of Transport for London operational data covering the entire network. "
            "Underground train positions and arrival predictions are updated every 30 seconds. "
            "Bus GPS positions, route adherence, and stop ETAs refresh every 10 seconds. "
            "Road traffic incidents, closures, and congestion levels from SCOOT detectors are included. "
            "Historical data is retained for 24 months, enabling trend analysis and demand forecasting."
        ),
        "category": "Transportation",
        "provider": "Transport for London",
        "update_frequency": "Streaming",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["transport", "tfl", "underground", "bus", "traffic", "london", "realtime"],
        "schema_fields": [
            {"name": "line_id", "type": "text", "description": "TfL line identifier (e.g. central, jubilee)"},
            {"name": "vehicle_id", "type": "text", "description": "Individual vehicle identifier"},
            {"name": "current_location", "type": "text", "description": "Between-stop descriptor"},
            {"name": "destination", "type": "text", "description": "Final destination name"},
            {"name": "expected_arrival", "type": "timestamptz", "description": "Predicted arrival at next stop"},
            {"name": "towards", "type": "text", "description": "Direction of travel"},
            {"name": "platform_name", "type": "text", "description": "Platform or stop name"},
            {"name": "timestamp", "type": "timestamptz", "description": "Record creation time"},
        ],
        "sample_rows": [
            {"line_id": "central", "vehicle_id": "940GZZLUACT", "destination": "Ealing Broadway", "towards": "Ealing Broadway", "platform_name": "Westbound - Platform 1", "expected_arrival": "2025-03-21T09:14:30Z"},
            {"line_id": "jubilee", "vehicle_id": "940GZZLUWSM", "destination": "Stratford", "towards": "Stratford", "platform_name": "Eastbound - Platform 2", "expected_arrival": "2025-03-21T09:15:05Z"},
            {"line_id": "northern", "vehicle_id": "940GZZLUKNG", "destination": "Morden via Bank", "towards": "Morden", "platform_name": "Southbound - Platform 4", "expected_arrival": "2025-03-21T09:14:55Z"},
        ],
    },
    {
        "slug": "london-planning-applications",
        "title": "London Planning Applications & Real Estate",
        "description": "Aggregated planning applications from all 32 London boroughs, normalised into a single schema.",
        "long_description": (
            "Planning application data from all 32 London boroughs and the City of London, "
            "aggregated and normalised into a single consistent schema. Each record includes "
            "the full application details, decision outcomes, appeal results, and associated "
            "property information. Data is updated daily from each borough's planning portal. "
            "Invaluable for property developers, investors, and market researchers tracking "
            "development activity and land use change across Greater London."
        ),
        "category": "Real Estate",
        "provider": "Greater London Authority",
        "update_frequency": "Daily",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["planning", "real-estate", "property", "development", "gla", "boroughs", "land-use"],
        "schema_fields": [
            {"name": "application_ref", "type": "text", "description": "Borough-issued reference number"},
            {"name": "borough", "type": "text", "description": "London borough name"},
            {"name": "address", "type": "text", "description": "Site address"},
            {"name": "postcode", "type": "text", "description": "Postcode of site"},
            {"name": "uprn", "type": "text", "description": "Unique Property Reference Number"},
            {"name": "application_type", "type": "text", "description": "Full, Householder, Listed Building, etc."},
            {"name": "description", "type": "text", "description": "Development description"},
            {"name": "status", "type": "text", "description": "Pending, Approved, Refused, Appealed"},
            {"name": "decision_date", "type": "date", "description": "Date of decision"},
            {"name": "ward", "type": "text", "description": "Electoral ward"},
            {"name": "coordinates", "type": "jsonb", "description": "GeoJSON point geometry"},
        ],
        "sample_rows": [
            {"application_ref": "2024/1823/FUL", "borough": "Hackney", "address": "42 Dalston Lane, London", "postcode": "E8 3AZ", "application_type": "Full", "status": "Approved", "decision_date": "2025-02-14"},
            {"application_ref": "2024/0091/HH", "borough": "Richmond upon Thames", "address": "18 Kew Road, Richmond", "postcode": "TW9 2NA", "application_type": "Householder", "status": "Pending", "decision_date": None},
            {"application_ref": "2024/3301/LBC", "borough": "Westminster", "address": "Flat 4, 12 Belgrave Square", "postcode": "SW1X 8PH", "application_type": "Listed Building Consent", "status": "Approved", "decision_date": "2025-01-30"},
        ],
    },
    {
        "slug": "fca-regulatory-register",
        "title": "FCA Regulatory Register",
        "description": "Financial Conduct Authority register of authorised firms and individuals. Vital for compliance surveillance.",
        "long_description": (
            "The complete FCA Financial Services Register, updated daily, covering all authorised and "
            "registered firms, appointed representatives, and approved individuals operating in the UK "
            "financial services sector. Includes current and historic permissions, regulatory actions, "
            "warnings, and cancellations. Cross-referenced with Companies House data for a complete "
            "entity view. Essential for financial crime compliance, counterparty screening, and "
            "regulatory intelligence workflows."
        ),
        "category": "Financial Regulation",
        "provider": "Financial Conduct Authority",
        "update_frequency": "Daily",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["fca", "financial", "compliance", "aml", "kyc", "regulated-firms", "permissions"],
        "schema_fields": [
            {"name": "firm_reference", "type": "text", "description": "FCA firm reference number (FRN)"},
            {"name": "firm_name", "type": "text", "description": "Registered firm name"},
            {"name": "status", "type": "text", "description": "Authorised, Registered, Cancelled, etc."},
            {"name": "permissions", "type": "text[]", "description": "Array of regulated activity permissions"},
            {"name": "business_type", "type": "text", "description": "Type of regulated business"},
            {"name": "address", "type": "jsonb", "description": "Principal place of business"},
            {"name": "appointed_representatives", "type": "jsonb", "description": "Linked ARs"},
            {"name": "regulatory_actions", "type": "jsonb", "description": "Fines, restrictions, cancellations"},
            {"name": "companies_house_number", "type": "text", "description": "Linked CH number if applicable"},
            {"name": "effective_from", "type": "date", "description": "Date authorisation became effective"},
        ],
        "sample_rows": [
            {"firm_reference": "122702", "firm_name": "Barclays Bank PLC", "status": "Authorised", "business_type": "UK Credit Institution", "effective_from": "2001-12-01"},
            {"firm_reference": "165975", "firm_name": "Lloyds Bank PLC", "status": "Authorised", "business_type": "UK Credit Institution", "effective_from": "2001-12-01"},
            {"firm_reference": "994775", "firm_name": "Monzo Bank Limited", "status": "Authorised", "business_type": "UK Credit Institution", "effective_from": "2017-04-10"},
        ],
    },
    {
        "slug": "hm-land-registry",
        "title": "HM Land Registry — Title & Price Paid",
        "description": "Every registered property title in England & Wales, plus all residential transactions since 1995.",
        "long_description": (
            "Two complementary datasets from HM Land Registry combined into a single queryable surface. "
            "The Title Register covers all freehold and leasehold titles in England and Wales, including "
            "ownership details, charges, covenants, and easements. The Price Paid dataset records every "
            "residential property transaction since January 1995 — over 27 million records — with full "
            "address, price, property type, and tenure. Together they provide an unmatched view of "
            "property ownership and market activity across England and Wales."
        ),
        "category": "Real Estate",
        "provider": "HM Land Registry",
        "update_frequency": "Monthly",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["property", "land-registry", "title", "ownership", "price-paid", "transactions", "england-wales"],
        "schema_fields": [
            {"name": "title_number", "type": "text", "description": "Unique land registry title number"},
            {"name": "tenure", "type": "text", "description": "Freehold or Leasehold"},
            {"name": "address", "type": "text", "description": "Property address"},
            {"name": "postcode", "type": "text", "description": "Postcode"},
            {"name": "uprn", "type": "text", "description": "Unique Property Reference Number"},
            {"name": "proprietor_name", "type": "text", "description": "Registered owner name"},
            {"name": "proprietor_type", "type": "text", "description": "Individual, Corporate, etc."},
            {"name": "price_paid", "type": "integer", "description": "Transaction price in GBP"},
            {"name": "transaction_date", "type": "date", "description": "Date of transaction"},
            {"name": "property_type", "type": "text", "description": "Detached, Semi, Terraced, Flat, Other"},
            {"name": "new_build", "type": "boolean", "description": "Whether property was newly built"},
        ],
        "sample_rows": [
            {"title_number": "AGL100042", "tenure": "Freehold", "address": "14 Thornton Avenue, London", "postcode": "W4 1QG", "price_paid": 1250000, "transaction_date": "2024-11-08", "property_type": "Semi-Detached", "new_build": False},
            {"title_number": "TGL512891", "tenure": "Leasehold", "address": "Flat 7, Bermondsey Street, London", "postcode": "SE1 3XF", "price_paid": 485000, "transaction_date": "2024-12-03", "property_type": "Flat", "new_build": False},
            {"title_number": "AGL228347", "tenure": "Freehold", "address": "3 Primrose Hill Road, London", "postcode": "NW3 3AT", "price_paid": 3100000, "transaction_date": "2025-01-15", "property_type": "Detached", "new_build": False},
        ],
    },
    {
        "slug": "met-police-crime",
        "title": "Metropolitan Police Crime Data",
        "description": "Street-level crime and outcome data across all 32 London boroughs, updated monthly.",
        "long_description": (
            "Crime records reported to the Metropolitan Police across all 32 London boroughs and the "
            "City of London, updated monthly. Each record includes crime category, approximate location "
            "(anonymised to the nearest street), outcome (charged, under investigation, no further action), "
            "and the month of occurrence. Data spans from 2010 to present. Useful for risk modelling, "
            "insurance underwriting, site selection analysis, and public safety research."
        ),
        "category": "Public Safety",
        "provider": "Metropolitan Police",
        "update_frequency": "Monthly",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["crime", "police", "safety", "london", "borough", "outcomes", "street-level"],
        "schema_fields": [
            {"name": "crime_id", "type": "text", "description": "Anonymised crime identifier"},
            {"name": "month", "type": "text", "description": "Year-month of occurrence (YYYY-MM)"},
            {"name": "borough", "type": "text", "description": "London borough"},
            {"name": "lsoa_code", "type": "text", "description": "Lower Super Output Area code"},
            {"name": "lsoa_name", "type": "text", "description": "LSOA name"},
            {"name": "crime_type", "type": "text", "description": "Category: Burglary, Robbery, Violence, etc."},
            {"name": "last_outcome", "type": "text", "description": "Most recent case outcome"},
            {"name": "street_name", "type": "text", "description": "Anonymised nearest street"},
            {"name": "latitude", "type": "float", "description": "Approximate latitude"},
            {"name": "longitude", "type": "float", "description": "Approximate longitude"},
        ],
        "sample_rows": [
            {"month": "2025-02", "borough": "Camden", "crime_type": "Burglary", "last_outcome": "Under investigation", "street_name": "On or near Kentish Town Road", "latitude": 51.5497, "longitude": -0.1425},
            {"month": "2025-02", "borough": "Tower Hamlets", "crime_type": "Vehicle crime", "last_outcome": "No further action", "street_name": "On or near Whitechapel Road", "latitude": 51.5185, "longitude": -0.0637},
            {"month": "2025-02", "borough": "Hackney", "crime_type": "Anti-social behaviour", "last_outcome": None, "street_name": "On or near Broadway Market", "latitude": 51.5378, "longitude": -0.0574},
        ],
    },
    {
        "slug": "london-air-quality",
        "title": "London Air Quality Network",
        "description": "Continuous readings from 100+ monitoring stations across Greater London — NO\u2082, PM2.5, PM10, O\u2083.",
        "long_description": (
            "Hourly air quality readings from over 100 monitoring stations operated by the London Air Quality "
            "Network (LAQN) and TfL's roadside sensors. Pollutants covered include nitrogen dioxide (NO\u2082), "
            "fine particulate matter (PM2.5 and PM10), ozone (O\u2083), and carbon monoxide (CO). "
            "Data extends back to 1993 for many sites, providing one of the longest urban air quality "
            "time series in Europe. Used for ULEZ compliance analysis, health impact assessment, "
            "environmental due diligence, and ESG reporting."
        ),
        "category": "Environment",
        "provider": "London Air Quality Network / TfL",
        "update_frequency": "Hourly",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["air-quality", "environment", "pollution", "no2", "pm25", "ulez", "esg", "health"],
        "schema_fields": [
            {"name": "site_code", "type": "text", "description": "Monitoring site identifier"},
            {"name": "site_name", "type": "text", "description": "Station name and location"},
            {"name": "borough", "type": "text", "description": "London borough"},
            {"name": "timestamp", "type": "timestamptz", "description": "Reading timestamp (UTC)"},
            {"name": "no2_ugm3", "type": "float", "description": "Nitrogen dioxide \u00b5g/m\u00b3"},
            {"name": "pm25_ugm3", "type": "float", "description": "Fine particulate matter \u00b5g/m\u00b3"},
            {"name": "pm10_ugm3", "type": "float", "description": "Coarse particulate matter \u00b5g/m\u00b3"},
            {"name": "o3_ugm3", "type": "float", "description": "Ozone \u00b5g/m\u00b3"},
            {"name": "latitude", "type": "float", "description": "Station latitude"},
            {"name": "longitude", "type": "float", "description": "Station longitude"},
        ],
        "sample_rows": [
            {"site_code": "MY1", "site_name": "Marylebone Road", "borough": "Westminster", "timestamp": "2025-03-21T08:00:00Z", "no2_ugm3": 68.4, "pm25_ugm3": 12.1, "pm10_ugm3": 18.3},
            {"site_code": "BX2", "site_name": "Bexley Belvedere", "borough": "Bexley", "timestamp": "2025-03-21T08:00:00Z", "no2_ugm3": 22.1, "pm25_ugm3": 8.4, "pm10_ugm3": 14.1},
            {"site_code": "KC1", "site_name": "North Kensington", "borough": "Kensington and Chelsea", "timestamp": "2025-03-21T08:00:00Z", "no2_ugm3": 34.7, "pm25_ugm3": 10.9, "pm10_ugm3": 16.8},
        ],
    },
    {
        "slug": "electoral-register-london",
        "title": "London Electoral & Demographic Data",
        "description": "Ward-level electoral statistics, population estimates, and demographic breakdowns for Greater London.",
        "long_description": (
            "Aggregated electoral and demographic data at ward and LSOA level across all 33 London local "
            "authorities. Includes registered electorate counts, voter turnout by election, population "
            "estimates by age and sex, and key Census 2021 demographic indicators. "
            "Updated annually following the annual canvass and ONS mid-year estimates. "
            "Useful for market sizing, site catchment analysis, political research, and public sector planning."
        ),
        "category": "Demographics",
        "provider": "Greater London Authority / ONS",
        "update_frequency": "Annual",
        "status": "live",
        "access_methods": ["api", "snowflake"],
        "tags": ["demographics", "population", "electoral", "census", "wards", "gla", "ons"],
        "schema_fields": [
            {"name": "gss_code", "type": "text", "description": "Government Statistical Service geography code"},
            {"name": "ward_name", "type": "text", "description": "Electoral ward name"},
            {"name": "borough", "type": "text", "description": "Local authority"},
            {"name": "electorate", "type": "integer", "description": "Number of registered electors"},
            {"name": "population_estimate", "type": "integer", "description": "ONS mid-year population estimate"},
            {"name": "population_density", "type": "float", "description": "Persons per km\u00b2"},
            {"name": "median_age", "type": "float", "description": "Median age of residents"},
            {"name": "year", "type": "integer", "description": "Reference year"},
        ],
        "sample_rows": [
            {"gss_code": "E05000026", "ward_name": "Cantelowes", "borough": "Camden", "electorate": 11842, "population_estimate": 14320, "population_density": 12400.0, "median_age": 31.4, "year": 2024},
            {"gss_code": "E05000082", "ward_name": "Bethnal Green East", "borough": "Tower Hamlets", "electorate": 10531, "population_estimate": 13750, "population_density": 18200.0, "median_age": 29.8, "year": 2024},
            {"gss_code": "E05000397", "ward_name": "Richmond Hill", "borough": "Richmond upon Thames", "electorate": 9284, "population_estimate": 11100, "population_density": 4100.0, "median_age": 41.2, "year": 2024},
        ],
    },
]

CATEGORIES = sorted(set(d["category"] for d in DATASETS))


def seed_catalog():
    """Upsert all dataset definitions into Supabase. Safe to run on every deploy."""
    url = f"{SUPABASE_URL}/rest/v1/datasets"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    payload = []
    for d in DATASETS:
        row = dict(d)
        row["tags"] = d["tags"]
        row["access_methods"] = d["access_methods"]
        row["schema_fields"] = d["schema_fields"]
        row["sample_rows"] = d["sample_rows"]
        payload.append(row)
    r = httpx.post(url, json=payload, headers=headers)
    if r.status_code not in (200, 201):
        print(f"Warning: catalog seed failed: {r.status_code} {r.text[:200]}")
