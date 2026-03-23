import os
import httpx
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

def get_columns():
    url = f"{SUPABASE_URL}/rest/v1/datasets"
    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Accept": "application/json",
        "Range": "0-0"  # Just get one row or metadata
    }
    r = httpx.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data:
            print("Columns in 'datasets' table:", list(data[0].keys()))
        else:
            print("No data in table to infer columns.")
    else:
        print(f"Error: {r.status_code} {r.text}")

if __name__ == "__main__":
    get_columns()
