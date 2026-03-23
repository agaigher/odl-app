import os
from dotenv import load_dotenv
load_dotenv()
from app.supabase_db import db_select

def check_users():
    try:
        # Check memberships to see who is actually in an org
        m = db_select("memberships", {})
        print("Memberships found:", len(m))
        for row in m[:10]:
            print(f"Org: {row.get('org_id')}, User: {row.get('user_id')}, Email: {row.get('invited_email')}, Role: {row.get('role')}")
            
        # Check organisations
        o = db_select("organisations", {})
        print("\nOrganisations found:", len(o))
        for row in o[:5]:
            print(f"ID: {row['id']}, Name: {row['name']}, Slug: {row['slug']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
