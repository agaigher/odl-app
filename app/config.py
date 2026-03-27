"""
Centralised configuration — all environment variables loaded once.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Supabase ──
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# ── App ──
# Base URL with no trailing slash. For local dev, set e.g. APP_URL=http://127.0.0.1:8000 and
# add the same origin in Supabase → Authentication → URL Configuration (Site URL + Redirect URLs).
# Email confirmation links use APP_URL/auth/email-confirm (implicit flow; tokens are in the URL hash).
APP_URL = os.environ.get("APP_URL", "https://app.opendata.london").rstrip("/")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev_secret_change_in_prod")

# ── Snowflake OAuth ──
SNOWFLAKE_ACCOUNT = os.environ.get("SNOWFLAKE_ACCOUNT", "").lower().replace("_", "-")
SNOWFLAKE_CLIENT_ID = os.environ.get("SNOWFLAKE_CLIENT_ID", "")
SNOWFLAKE_CLIENT_SECRET = os.environ.get("SNOWFLAKE_CLIENT_SECRET", "")
SNOWFLAKE_REDIRECT_URI = f"{APP_URL}/auth/snowflake/callback"

# ── Stripe ──
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "sk_test_dummy")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_dummy")


