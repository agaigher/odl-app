from fasthtml.common import *

# Initialize SQLite database — use /tmp on Vercel (read-only filesystem), data/ locally
import os
db_path = '/tmp/odl_app.db' if os.environ.get('VERCEL') else 'data/odl_app.db'
db = database(db_path)

# Define core tables for our MVP (Users, Datasets, API Keys, Data Shares)
users_tbl = db.t.users
if users_tbl not in db.t:
    users_tbl.create(id=int, email=str, name=str, hashed_password=str, role=str, pk='id')

datasets_tbl = db.t.datasets
if datasets_tbl not in db.t:
    datasets_tbl.create(id=int, slug=str, name=str, description=str, category=str, update_frequency=str, provider=str, pk='id')

api_keys_tbl = db.t.api_keys
if api_keys_tbl not in db.t:
    api_keys_tbl.create(id=int, user_id=int, key_name=str, api_key_hash=str, created_at=str, last_used=str, pk='id')

data_shares_tbl = db.t.data_shares
if data_shares_tbl not in db.t:
    data_shares_tbl.create(id=int, user_id=int, snowflake_account=str, share_name=str, db_name=str, status=str, pk='id')

# Seed some initial datasets if empty
def seed_datasets():
    if datasets_tbl.count == 0:
        datasets_tbl.insert(
            slug="uk-companies-house",
            name="UK Companies House (Live)",
            description="Continuously updated registry of all UK corporate entities, directors, and filings. Synchronized sub-second.",
            category="Corporate Registries",
            update_frequency="Real-time",
            provider="Companies House"
        )
        datasets_tbl.insert(
            slug="tfl-transport-network",
            name="TfL Transport Network & Telemetry",
            description="Live feeds of London Underground, buses, and road traffic incidents.",
            category="Transportation",
            update_frequency="Streaming",
            provider="Transport for London"
        )
        datasets_tbl.insert(
            slug="london-planning-applications",
            name="London Planning Applications & Real Estate",
            description="Aggregated planning applications from all 32 London boroughs, normalized into a single schema.",
            category="Real Estate",
            update_frequency="Daily",
            provider="Greater London Authority"
        )
        datasets_tbl.insert(
            slug="fca-regulatory-register",
            name="FCA Regulatory Register",
            description="Financial Conduct Authority register of authorized firms and individuals. Vital for compliance surveillance.",
            category="Financial Regulation",
            update_frequency="Daily",
            provider="FCA"
        )
seed_datasets()
