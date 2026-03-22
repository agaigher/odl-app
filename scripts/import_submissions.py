"""
Import dataset CSV submissions into the Supabase datasets table.

Usage:
    python scripts/import_submissions.py
    python scripts/import_submissions.py "Dataset Research"
    python scripts/import_submissions.py data-submissions "Dataset Research"

Scans the given folders (default: data-submissions) for CSV files,
parses each row, and upserts into Supabase on slug conflict.
Processed files are listed in the summary — move them to an archive
folder manually once you're happy with the import.

Requires: SUPABASE_URL and SUPABASE_SERVICE_KEY in .env or environment.
"""

import os
import sys
import csv
import json
import httpx
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_URL or not SERVICE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    sys.exit(1)


# ── Field parsers ─────────────────────────────────────────────────────────────

def parse_tags(value: str) -> list:
    if not value:
        return []
    return [t.strip().lower() for t in value.split(",") if t.strip()]


def parse_access_methods(value: str) -> list:
    v = (value or "").strip().lower()
    if v == "both":
        return ["api", "snowflake"]
    if v == "snowflake":
        return ["snowflake"]
    return ["api"]


def parse_schema_fields(value: str) -> list:
    """
    Expects semicolon-separated entries, each in format:
    FieldName|type|description
    Returns a list of dicts: [{name, type, description}, ...]
    """
    if not value:
        return []
    fields = []
    for entry in value.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("|", 2)
        if len(parts) == 3:
            fields.append({
                "name": parts[0].strip(),
                "type": parts[1].strip(),
                "description": parts[2].strip(),
            })
        elif len(parts) == 2:
            fields.append({"name": parts[0].strip(), "type": parts[1].strip(), "description": ""})
        elif len(parts) == 1:
            fields.append({"name": parts[0].strip(), "type": "string", "description": ""})
    return fields


def parse_sample_rows(value: str) -> list:
    """
    Expects semicolon-separated rows, each row being a comma-separated string.
    Returns a list of row strings (kept as-is for display purposes).
    """
    if not value:
        return []
    return [r.strip() for r in value.split(";") if r.strip()]


def row_to_dataset(row: dict) -> dict:
    return {
        "slug": (row.get("slug") or "").strip().lower(),
        "title": (row.get("title") or "").strip(),
        "description": (row.get("short_description") or "").strip(),
        "long_description": (row.get("long_description") or "").strip() or None,
        "category": (row.get("category") or "").strip() or None,
        "provider": (row.get("provider") or "").strip() or None,
        "update_frequency": (row.get("update_frequency") or "").strip() or None,
        "status": "live",
        "tags": parse_tags(row.get("tags", "")),
        "access_methods": parse_access_methods(row.get("access_type", "api")),
        "schema_fields": parse_schema_fields(row.get("schema_fields", "")),
        "sample_rows": parse_sample_rows(row.get("sample_rows", "")),
    }


# ── Supabase upsert ───────────────────────────────────────────────────────────

def upsert_batch(datasets: list) -> list:
    """Upsert a single batch into Supabase. Raises on error."""
    url = f"{SUPABASE_URL}/rest/v1/datasets?on_conflict=slug"
    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    r = httpx.post(url, json=datasets, headers=headers, timeout=60)
    if not r.is_success:
        print(f"    Response body: {r.text[:500]}")
        r.raise_for_status()
    return r.json()


def upsert_datasets(datasets: list, batch_size: int = 20) -> int:
    """Upsert in batches. Returns total count upserted."""
    total = 0
    for i in range(0, len(datasets), batch_size):
        batch = datasets[i:i + batch_size]
        slugs = [d["slug"] for d in batch]
        print(f"    Batch {i // batch_size + 1}: {slugs[0]} … {slugs[-1]}")
        try:
            result = upsert_batch(batch)
            total += len(result) if isinstance(result, list) else len(batch)
        except Exception as e:
            print(f"    Batch failed, trying rows individually...")
            for ds in batch:
                try:
                    upsert_batch([ds])
                    total += 1
                    print(f"      ok: {ds['slug']}")
                except Exception as e2:
                    print(f"      SKIP {ds['slug']}: {e2}")
    return total


# ── Main ──────────────────────────────────────────────────────────────────────

def import_folder(folder: Path) -> tuple[int, int, list]:
    """Import all CSVs in a folder. Returns (imported, skipped, errors)."""
    csvs = sorted(folder.glob("*.csv"))
    if not csvs:
        print(f"  No CSV files found in {folder}")
        return 0, 0, []

    all_datasets = []
    skipped = []
    errors = []

    for csv_path in csvs:
        print(f"  Reading {csv_path.name}...")
        try:
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            for i, row in enumerate(rows, 1):
                slug = (row.get("slug") or "").strip().lower()
                if not slug:
                    skipped.append(f"{csv_path.name} row {i}: missing slug")
                    continue
                title = (row.get("title") or "").strip()
                if not title:
                    skipped.append(f"{csv_path.name} row {i} ({slug}): missing title")
                    continue
                all_datasets.append(row_to_dataset(row))
                print(f"    + {slug}")

        except Exception as e:
            errors.append(f"{csv_path.name}: {e}")
            print(f"  ERROR reading {csv_path.name}: {e}")

    if not all_datasets:
        return 0, len(skipped), errors

    print(f"\n  Upserting {len(all_datasets)} datasets to Supabase...")
    try:
        count = upsert_datasets(all_datasets)
        print(f"  Done — {count} rows upserted.")
        return count, len(skipped), errors
    except Exception as e:
        errors.append(f"Upsert failed: {e}")
        print(f"  ERROR during upsert: {e}")
        return 0, len(skipped), errors


def main():
    base = Path(__file__).parent.parent

    # Folders to scan — defaults, overridden by CLI args
    if len(sys.argv) > 1:
        folders = [base / arg for arg in sys.argv[1:]]
    else:
        folders = [base / "data-submissions"]

    total_imported = 0
    total_skipped = 0
    all_errors = []

    for folder in folders:
        if not folder.exists():
            print(f"Folder not found: {folder}")
            continue
        print(f"\nScanning: {folder}")
        imported, skipped, errors = import_folder(folder)
        total_imported += imported
        total_skipped += skipped
        all_errors.extend(errors)

    print(f"\n{'='*50}")
    print(f"Total imported : {total_imported}")
    print(f"Total skipped  : {total_skipped}")
    print(f"Errors         : {len(all_errors)}")
    if all_errors:
        print("\nErrors:")
        for e in all_errors:
            print(f"  - {e}")
    if total_skipped:
        print(f"\nSkipped rows were missing slug or title — check the CSV.")


if __name__ == "__main__":
    main()
