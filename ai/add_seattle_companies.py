import os
import sys
from pathlib import Path

# Add current folder to sys.path to resolve local imports
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from db import SessionLocal, Company, init_db

# Clean list of 100 companies from the Seattle PDF
companies_list = [
    {"name": "Amazon / AWS", "careers_url": "https://amazon.jobs"},
    {"name": "Microsoft", "careers_url": "https://careers.microsoft.com"},
    {"name": "Expedia Group", "careers_url": "https://lifeatexpedia.com"},
    {"name": "Nordstrom", "careers_url": "https://careers.nordstrom.com"},
    {"name": "Starbucks", "careers_url": "https://careers.starbucks.com"},
    {"name": "Boeing", "careers_url": "https://boeing.com/careers"},
    {"name": "T-Mobile", "careers_url": "https://careers.t-mobile.com"},
    {"name": "Paccar", "careers_url": "https://paccar.com/careers"},
    {"name": "Weyerhaeuser", "careers_url": "https://weyerhaeuser.com/company/careers"},
    {"name": "Costco", "careers_url": "https://costco.com/jobs"},
    {"name": "Alaska Airlines", "careers_url": "https://jobs.alaskaair.com"},
    {"name": "REI", "careers_url": "https://rei.com/careers"},
    {"name": "Google", "careers_url": "https://careers.google.com"},
    {"name": "Meta", "careers_url": "https://metacareers.com"},
    {"name": "Salesforce", "careers_url": "https://salesforce.com/company/careers"},
    {"name": "Oracle", "careers_url": "https://careers.oracle.com"},
    {"name": "Tableau (Salesforce)", "careers_url": "https://salesforce.com/company/careers"},
    {"name": "SAP", "careers_url": "https://sap.com/careers"},
    {"name": "Zendesk", "careers_url": "https://careers.zendesk.com"},
    {"name": "DocuSign", "careers_url": "https://docusign.com/company/careers"},
    {"name": "Smartsheet", "careers_url": "https://smartsheet.com/company/careers"},
    {"name": "Avalara", "careers_url": "https://avalara.com/us/en/about/careers"},
    {"name": "Zones", "careers_url": "https://zones.com/careers"},
    {"name": "WatchGuard Technologies", "careers_url": "https://watchguard.com/wgrd-about/careers"},
    {"name": "Zerto (HPE)", "careers_url": "https://hpe.com/us/en/living-progress/careers"},
    {"name": "Concur (SAP)", "careers_url": "https://careers.sap.com"},
    {"name": "F5 Networks", "careers_url": "https://f5.com/company/careers"},
    {"name": "Nintex", "careers_url": "https://nintex.com/careers"},
    {"name": "Allen Institute for AI (Ai2)", "careers_url": "https://allenai.org/careers"},
    {"name": "Turi (Apple)", "careers_url": "https://jobs.apple.com"},
    {"name": "Vast Data", "careers_url": "https://vastdata.com/careers"},
    {"name": "Weights and Biases", "careers_url": "https://wandb.ai/careers"},
    {"name": "Algorithmia (DataRobot)", "careers_url": "https://datarobot.com/careers"},
    {"name": "SparkCognition", "careers_url": "https://sparkcognition.com/careers"},
    {"name": "Nautilus Biotechnology", "careers_url": "https://nautilustechnologies.com/careers"},
    {"name": "Carbon Black (VMware)", "careers_url": "https://broadcom.com/company/careers"},
    {"name": "Lucd", "careers_url": "https://lucd.ai"},
    {"name": "Narrative Science", "careers_url": "https://narrativescience.com"},
    {"name": "Qumulo", "careers_url": "https://qumulo.com/careers"},
    {"name": "Syntropy", "careers_url": "https://syntropynet.com"},
    {"name": "Wavenet", "careers_url": "https://wavenet.com/careers"},
    {"name": "Adaptive Biotechnologies", "careers_url": "https://adaptivebiotech.com/careers"},
    {"name": "BioAtla", "careers_url": "https://bioatla.com/careers"},
    {"name": "Nuvation Bio", "careers_url": "https://nuvationbio.com/careers"},
    {"name": "Ichor Life Sciences", "careers_url": "https://ichortherapeutics.com/careers"},
    {"name": "Juno Therapeutics (BMS)", "careers_url": "https://juno.com/careers"},
    {"name": "Stripe", "careers_url": "https://stripe.com/jobs"},
    {"name": "Remitly", "careers_url": "https://remitly.com/us/en/home/careers"},
    {"name": "Gravity Payments", "careers_url": "https://gravitypayments.com/careers"},
    {"name": "Zipwhip (Twilio)", "careers_url": "https://twilio.com/company/jobs"},
    {"name": "Accolade", "careers_url": "https://accoladecare.com/about/careers"},
    {"name": "Concord Technologies", "careers_url": "https://concordfax.com/careers"},
    {"name": "Fareportal", "careers_url": "https://fareportal.com/careers"},
    {"name": "Vacasa", "careers_url": "https://vacasa.com/careers"},
    {"name": "Rover.com", "careers_url": "https://rover.com/careers"},
    {"name": "Zulily (Qurate)", "careers_url": "https://zulily.com/careers"},
    {"name": "Chewy", "careers_url": "https://chewy.com/jobs"},
    {"name": "OfferUp", "careers_url": "https://offerup.com/careers"},
    {"name": "Redfin", "careers_url": "https://redfin.com/about/jobs"},
    {"name": "Zillow", "careers_url": "https://zillow.com/careers"},
    {"name": "Porch Group", "careers_url": "https://porchgroup.com/careers"},
    {"name": "Convoy", "careers_url": "https://convoy.com/careers"},
    {"name": "Flexe", "careers_url": "https://flexe.com/careers"},
    {"name": "Shippo", "careers_url": "https://goshippo.com/careers"},
    {"name": "Limeade", "careers_url": "https://limeade.com/about/careers"},
    {"name": "Providence Health", "careers_url": "https://careers.providence.org"},
    {"name": "Swedish Medical Center", "careers_url": "https://swedish.org/careers"},
    {"name": "UW Medicine", "careers_url": "https://careers.uwmedicine.org"},
    {"name": "Seattle Children's Hospital", "careers_url": "https://seattlechildrens.org/about/careers"},
    {"name": "Fred Hutchinson Cancer Center", "careers_url": "https://fredhutch.org/careers"},
    {"name": "Seagen (Pfizer)", "careers_url": "https://pfizer.com/about/careers"},
    {"name": "Immunomedics (Gilead)", "careers_url": "https://jobs.gilead.com"},
    {"name": "Athira Pharma", "careers_url": "https://athirapharma.com/about/careers"},
    {"name": "Omeros", "careers_url": "https://omeros.com/about-us/careers"},
    {"name": "Sana Biotechnology", "careers_url": "https://sana.com/careers"},
    {"name": "Oncobiologics", "careers_url": "https://oncobiologics.com"},
    {"name": "WellSky", "careers_url": "https://wellsky.com/careers"},
    {"name": "Apixio", "careers_url": "https://apixio.com/company/careers"},
    {"name": "Kyowa Kirin", "careers_url": "https://kyowakirin.com/careers"},
    {"name": "Outreach", "careers_url": "https://outreach.io/company/careers"},
    {"name": "Highspot", "careers_url": "https://highspot.com/careers"},
    {"name": "Icertis", "careers_url": "https://icertis.com/company/careers"},
    {"name": "Apttus (Conga)", "careers_url": "https://conga.com/careers"},
    {"name": "Auth0 (Okta)", "careers_url": "https://okta.com/company/careers"},
    {"name": "Pushpay", "careers_url": "https://pushpay.com/careers"},
    {"name": "WP Engine", "careers_url": "https://wpengine.com/careers"},
    {"name": "Hiya", "careers_url": "https://hiya.com/careers"},
    {"name": "Limelight Networks", "careers_url": "https://limelight.com/careers"},
    {"name": "Formant", "careers_url": "https://formant.io/careers"},
    {"name": "Outrider", "careers_url": "https://outrider.ai/careers"},
    {"name": "Saildrone", "careers_url": "https://saildrone.com/careers"},
    {"name": "Tune", "careers_url": "https://help.tune.com/hc/en-us/articles/partners"},
    {"name": "Mighty Networks", "careers_url": "https://mightynetworks.com/jobs"},
    {"name": "Helion Energy", "careers_url": "https://helionenergy.com/careers"},
    {"name": "Rad Power Bikes", "careers_url": "https://radpowerbikes.com/pages/careers"},
    {"name": "MedBridge", "careers_url": "https://medbridgeeducation.com/careers"},
    {"name": "Jobber", "careers_url": "https://getjobber.com/careers"},
    {"name": "Boundless Immigration", "careers_url": "https://boundless.com/about/careers"},
    {"name": "CrowdStreet", "careers_url": "https://crowdstreet.com/about/careers"}
]

def add_companies():
    print("Connecting to database...")
    db = SessionLocal()
    
    try:
        # Fetch existing names/URLs to prevent duplicates
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
