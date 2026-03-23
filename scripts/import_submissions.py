import os
import csv
import json
import httpx
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

DATA_SUBMISSIONS_DIR = Path("data-submissions")
DATA_SUBMITTED_DIR = Path("data-submitted")

def _headers():
    return {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }

def parse_schema_fields(schema_str):
    """
    Parses 'name|type|description; name|type|description' format.
    """
    if not schema_str or schema_str.upper() == "UNKNOWN":
        return []
    
    fields = []
    parts = [p.strip() for p in schema_str.split(";") if p.strip()]
    for p in parts:
        sub_parts = [sp.strip() for sp in p.split("|")]
        if len(sub_parts) >= 2:
            fields.append({
                "name": sub_parts[0],
                "type": sub_parts[1],
                "description": sub_parts[2] if len(sub_parts) > 2 else ""
            })
    return fields

def parse_sample_rows(sample_str, schema_fields):
    """
    Parses 'val1|val2|...; val4|val5|...' format using keys from schema_fields.
    """
    if not sample_str or sample_str.upper() == "UNKNOWN":
        return []
    
    rows = []
    keys = [f["name"] for f in schema_fields]
    line_parts = [lp.strip() for lp in sample_str.split(";") if lp.strip()]
    
    for lp in line_parts:
        vals = [v.strip() for v in lp.split("|")]
        row_dict = {}
        for i, k in enumerate(keys):
            if i < len(vals):
                row_dict[k] = vals[i]
        if row_dict:
            rows.append(row_dict)
    return rows

def parse_access_methods(access_type):
    """
    Maps access_type (api, snowflake, both) to list of methods.
    """
    access_type = (access_type or "").lower().strip()
    if access_type == "api":
        return ["api"]
    elif access_type == "snowflake":
        return ["snowflake"]
    elif access_type == "both":
        return ["api", "snowflake"]
    return ["api"] # Default

def process_csv(file_path):
    print(f"Processing {file_path}...")
    
    payload = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            schema_fields = parse_schema_fields(row.get("schema_fields", ""))
            
            # Map CSV columns to DB columns
            record = {
                "title": row.get("title"),
                "slug": row.get("slug"),
                "description": row.get("short_description"),
                "long_description": row.get("long_description"),
                "category": row.get("category"),
                "provider": row.get("provider"),
                "update_frequency": row.get("update_frequency"),
                "status": row.get("status", "live"),
                "tags": [t.strip() for t in row.get("tags", "").split(",") if t.strip()],
                "access_methods": parse_access_methods(row.get("access_type")),
                "schema_fields": schema_fields,
                "sample_rows": parse_sample_rows(row.get("sample_rows", ""), schema_fields)
            }
            payload.append(record)

    if not payload:
        print(f"No records found in {file_path}")
        return False

    # Upsert into Supabase
    url = f"{SUPABASE_URL}/rest/v1/datasets?on_conflict=slug"
    try:
        r = httpx.post(url, json=payload, headers=_headers())
        r.raise_for_status()
        print(f"Successfully upserted {len(payload)} records from {file_path}")
        return True
    except Exception as e:
        print(f"Error upserting data from {file_path}: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False

def main():
    if not DATA_SUBMISSIONS_DIR.exists():
        print(f"Directory {DATA_SUBMISSIONS_DIR} does not exist.")
        return

    if not DATA_SUBMITTED_DIR.exists():
        DATA_SUBMITTED_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = list(DATA_SUBMISSIONS_DIR.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in data-submissions.")
        return

    for csv_file in csv_files:
        # Skip template or zero-byte files if needed
        if csv_file.name == "template.csv":
            print(f"Skipping template file: {csv_file.name}")
            continue
            
        success = process_csv(csv_file)
        if success:
            # Move file to data-submitted
            dest = DATA_SUBMITTED_DIR / csv_file.name
            try:
                shutil.move(str(csv_file), str(dest))
                print(f"Moved {csv_file.name} to {DATA_SUBMITTED_DIR}")
            except Exception as e:
                print(f"Error moving {csv_file.name}: {e}")

if __name__ == "__main__":
    main()
