import json
import os
import sys
from pathlib import Path

# Add current folder to sys.path to resolve local imports
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from db import init_db, SessionLocal, Company

def migrate():
    # Make sure tables exist
    print("Initializing database schema...")
    init_db()
    
    companies_json_path = current_dir / "config" / "companies.json"
    if not companies_json_path.exists():
        print(f"Error: companies.json not found at {companies_json_path}")
        sys.exit(1)
        
    print(f"Reading companies from {companies_json_path}...")
    with open(companies_json_path, "r", encoding="utf-8") as f:
        try:
            companies_data = json.load(f)
        except Exception as e:
            print(f"Error parsing companies.json: {e}")
            sys.exit(1)
            
    print(f"Found {len(companies_data)} companies in JSON file.")
    
    db = SessionLocal()
    try:
        # Get existing companies to avoid duplicates
        existing_tokens = {c.token for c in db.query(Company).all() if c.token}
        existing_names = {c.name.lower() for c in db.query(Company).all()}
        
        added_count = 0
        skipped_count = 0
        
        for item in companies_data:
            name = item.get("name", "").strip()
            ats = item.get("ats", "").strip().lower()
            token = item.get("token", "").strip().lower() if item.get("token") else None
            careers_url = item.get("careers_url", "").strip()
            
            if not name or not ats:
                print(f"Skipping invalid record: {item}")
                skipped_count += 1
                continue
                
            # Duplicate check
            is_dup = False
            if name.lower() in existing_names:
                is_dup = True
            elif token and token in existing_tokens:
                is_dup = True
                
            if is_dup:
                skipped_count += 1
                continue
                
            company = Company(
                name=name,
                ats=ats,
                token=token,
                careers_url=careers_url
            )
            db.add(company)
            
            # Keep tracking sets up to date
            existing_names.add(name.lower())
            if token:
                existing_tokens.add(token)
                
            added_count += 1
            
        if added_count > 0:
            db.commit()
            print(f"Successfully migrated {added_count} companies to the database.")
        else:
            print("No new companies to migrate.")
            
        print(f"Migration summary: {added_count} added, {skipped_count} skipped/duplicates.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during migration transaction: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
