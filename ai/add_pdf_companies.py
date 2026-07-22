import os
import sys
from pathlib import Path

# Add current folder to sys.path to resolve local imports
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from db import SessionLocal, Company, init_db

# Clean list of 75 companies from the PDF
companies_list = [
    {"name": "Penn Medicine", "careers_url": "https://careers.pennmedicine.org"},
    {"name": "Children's Hospital of Philadelphia (CHOP)", "careers_url": "https://jobs.chop.edu"},
    {"name": "Jefferson Health", "careers_url": "https://jefferson.edu/about/careers"},
    {"name": "Temple University Hospital", "careers_url": "https://templehealthcareers.com"},
    {"name": "Main Line Health", "careers_url": "https://mainlinehealth.org/careers"},
    {"name": "Doylestown Health", "careers_url": "https://dh.org/careers"},
    {"name": "Tower Health", "careers_url": "https://towerhealth.org/careers"},
    {"name": "Independence Blue Cross", "careers_url": "https://ibx.com/about/careers"},
    {"name": "Cigna / Evernorth", "careers_url": "https://careers.cigna.com"},
    {"name": "Aetna (CVS Health)", "careers_url": "https://jobs.cvshealth.com"},
    {"name": "UnitedHealth / Optum", "careers_url": "https://careers.unitedhealthgroup.com"},
    {"name": "IQVIA", "careers_url": "https://jobs.iqvia.com"},
    {"name": "BRT Analytics (Cerner)", "careers_url": "https://oracle.com/careers"},
    {"name": "Cotiviti", "careers_url": "https://cotiviti.com/careers"},
    {"name": "Privia Health", "careers_url": "https://priviahealth.com/careers"},
    {"name": "Medidata (Dassault)", "careers_url": "https://medidata.com/careers"},
    {"name": "Johnson and Johnson", "careers_url": "https://jobs.jnj.com"},
    {"name": "Merck and Co.", "careers_url": "https://jobs.merck.com"},
    {"name": "GlaxoSmithKline (GSK)", "careers_url": "https://gsk.com/en-gb/careers"},
    {"name": "AstraZeneca", "careers_url": "https://astrazeneca.com/our-company/careers"},
    {"name": "Bristol Myers Squibb", "careers_url": "https://careers.bms.com"},
    {"name": "Novo Nordisk", "careers_url": "https://novonordisk-us.com/careers"},
    {"name": "Lonza", "careers_url": "https://lonza.com/about/careers"},
    {"name": "Catalent", "careers_url": "https://catalent.com/careers"},
    {"name": "West Pharmaceutical Services", "careers_url": "https://westpharma.com/about-us/careers"},
    {"name": "Incyte Corporation", "careers_url": "https://incyte.com/careers"},
    {"name": "Inovio Pharmaceuticals", "careers_url": "https://inovio.com/about-us/careers"},
    {"name": "Trevena", "careers_url": "https://trevena.com/careers"},
    {"name": "Shire (Takeda) PA", "careers_url": "https://takeda.com/en-us/careers"},
    {"name": "Guardant Health", "careers_url": "https://guardanthealth.com/careers"},
    {"name": "Comcast / NBCUniversal", "careers_url": "https://jobs.comcast.com"},
    {"name": "SAP", "careers_url": "https://careers.sap.com"},
    {"name": "Oracle", "careers_url": "https://careers.oracle.com"},
    {"name": "Microsoft", "careers_url": "https://careers.microsoft.com"},
    {"name": "Google", "careers_url": "https://careers.google.com"},
    {"name": "IBM", "careers_url": "https://ibm.com/employment"},
    {"name": "Unisys", "careers_url": "https://unisys.com/careers"},
    {"name": "Conduent", "careers_url": "https://careers.conduent.com"},
    {"name": "Virtusa", "careers_url": "https://virtusa.com/careers"},
    {"name": "Infosys", "careers_url": "https://infosys.com/careers"},
    {"name": "Cognizant", "careers_url": "https://careers.cognizant.com"},
    {"name": "TCS", "careers_url": "https://tcs.com/careers"},
    {"name": "Wipro", "careers_url": "https://wipro.com/careers"},
    {"name": "Radial", "careers_url": "https://radial.com/careers"},
    {"name": "Evolent Health", "careers_url": "https://evolenthealth.com/about/careers"},
    {"name": "DXC Technology", "careers_url": "https://careers.dxc.com"},
    {"name": "Vanguard", "careers_url": "https://vanguardjobs.com"},
    {"name": "Lincoln Financial Group", "careers_url": "https://careers.lincolnfinancial.com"},
    {"name": "Prudential Financial", "careers_url": "https://prudential.com/links/about/careers"},
    {"name": "SEI Investments", "careers_url": "https://seic.com/about-sei/careers"},
    {"name": "Janney Montgomery Scott", "careers_url": "https://janney.com/about-us/careers"},
    {"name": "The Reinvestment Fund", "careers_url": "https://reinvestment.com/careers"},
    {"name": "Incenter Financial Group", "careers_url": "https://incenterglobal.com/careers"},
    {"name": "Susquehanna International Group", "careers_url": "https://sig.com/careers"},
    {"name": "Conifer Financial Services", "careers_url": "https://coniferfs.com/careers"},
    {"name": "Verisk Analytics", "careers_url": "https://careers.verisk.com"},
    {"name": "FS Investments", "careers_url": "https://fsinvestments.com/about/careers"},
    {"name": "Hamilton Lane", "careers_url": "https://hamiltonlane.com/en-us/careers"},
    {"name": "Beneficial Bank", "careers_url": "https://mybeneficial.com/careers"},
    {"name": "Republic Bank", "careers_url": "https://myrepublicbank.com/about/careers"},
    {"name": "Deloitte", "careers_url": "https://deloitte.com/us/en/careers"},
    {"name": "Accenture", "careers_url": "https://accenture.com/us-en/careers"},
    {"name": "PwC", "careers_url": "https://pwc.com/us/en/careers"},
    {"name": "EY", "careers_url": "https://ey.com/en_us/careers"},
    {"name": "KPMG", "careers_url": "https://kpmg.com/us/en/careers"},
    {"name": "Aramark", "careers_url": "https://aramark.com/careers"},
    {"name": "Crown Holdings", "careers_url": "https://crowncork.com/about/careers"},
    {"name": "Tyco (Johnson Controls)", "careers_url": "https://johnsoncontrols.com/careers"},
    {"name": "Day and Zimmermann", "careers_url": "https://dayzim.com/careers"},
    {"name": "Charming Shoppes (Ascena)", "careers_url": "https://ascenarsg.com/careers"},
    {"name": "Urban Outfitters", "careers_url": "https://urbn.com/careers"},
    {"name": "AmeriHealth Caritas", "careers_url": "https://amerihealthcaritas.com/careers"},
    {"name": "Radian Group", "careers_url": "https://radian.com/about-us/careers"},
    {"name": "GSI Commerce (eBay)", "careers_url": "https://ebayinc.com/careers"}
]

def add_companies():
    print("Connecting to database...")
    db = SessionLocal()
    
    try:
        # Fetch existing names to prevent duplicates
        existing_names = {c.name.lower() for c in db.query(Company).all()}
        existing_urls = {c.careers_url.lower() for c in db.query(Company).all() if c.careers_url}
        
        added_count = 0
        skipped_count = 0
        
        for comp in companies_list:
            name = comp["name"].strip()
            url = comp["careers_url"].strip()
            
            # Simple duplicate check
            if name.lower() in existing_names or url.lower() in existing_urls:
                print(f"Skipping (already exists): {name}")
                skipped_count += 1
                continue
            
            company = Company(
                name=name,
                ats="playwright",
                careers_url=url
            )
            db.add(company)
            
            # Update local tracking sets
            existing_names.add(name.lower())
            existing_urls.add(url.lower())
            
            added_count += 1
            print(f"Adding: {name} ({url})")
            
        if added_count > 0:
            db.commit()
            print(f"\nSuccessfully added {added_count} new companies to the database.")
        else:
            print("\nNo new companies were added (all exist in database).")
            
        print(f"Summary: {added_count} added, {skipped_count} skipped.")
        
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    add_companies()
