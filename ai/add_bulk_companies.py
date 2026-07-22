import os
import sys
from pathlib import Path

# Add current folder to sys.path to resolve local imports
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from db import SessionLocal, Company

# Healthcare Data Analyst Companies (85)
healthcare_list = [
    {"name": "UnitedHealth Group / Optum", "careers_url": "https://careers.unitedhealthgroup.com"},
    {"name": "CVS Health / Aetna", "careers_url": "https://jobs.cvshealth.com"},
    {"name": "Cigna / Evernorth", "careers_url": "https://careers.cigna.com"},
    {"name": "Elevance Health", "careers_url": "https://careers.elevancehealth.com"},
    {"name": "Humana", "careers_url": "https://careers.humana.com"},
    {"name": "Centene Corporation", "careers_url": "https://careers.centene.com"},
    {"name": "Molina Healthcare", "careers_url": "https://careers.molinahealthcare.com"},
    {"name": "Kaiser Permanente", "careers_url": "https://jobs.kaiserpermanente.org"},
    {"name": "Blue Cross Blue Shield affiliates", "careers_url": "https://bcbs.com/careers"},
    {"name": "Health Care Service Corp (HCSC)", "careers_url": "https://hcsc.com/careers"},
    {"name": "Blue Shield of California", "careers_url": "https://blueshieldca.com/careers"},
    {"name": "Highmark Health", "careers_url": "https://highmarkhealth.org/careers"},
    {"name": "GuideWell / Florida Blue", "careers_url": "https://guidewell.com/careers"},
    {"name": "EmblemHealth", "careers_url": "https://emblemhealth.com/careers"},
    {"name": "Healthfirst", "careers_url": "https://healthfirst.org/careers"},
    {"name": "SCAN Health Plan", "careers_url": "https://scanhealthplan.com/careers"},
    {"name": "Alignment Health", "careers_url": "https://alignmenthealth.com/careers"},
    {"name": "Devoted Health", "careers_url": "https://devoted.com/careers"},
    {"name": "Clover Health", "careers_url": "https://cloverhealth.com/careers"},
    {"name": "Oscar Health", "careers_url": "https://hioscar.com/careers"},
    {"name": "HCA Healthcare", "careers_url": "https://careers.hcahealthcare.com"},
    {"name": "Tenet Healthcare", "careers_url": "https://careers.tenethealth.com"},
    {"name": "CommonSpirit Health", "careers_url": "https://commonspirit.careers"},
    {"name": "Ascension", "careers_url": "https://ascension.org/careers"},
    {"name": "Providence", "careers_url": "https://providence.jobs"},
    {"name": "Advocate Health", "careers_url": "https://advocatehealth.com/careers"},
    {"name": "Trinity Health", "careers_url": "https://trinity-health.org/careers"},
    {"name": "Sutter Health", "careers_url": "https://sutterhealth.org/careers"},
    {"name": "Mayo Clinic", "careers_url": "https://jobs.mayoclinic.org"},
    {"name": "Cleveland Clinic", "careers_url": "https://jobs.clevelandclinic.org"},
    {"name": "Johns Hopkins Medicine", "careers_url": "https://jobs.hopkinsmedicine.org"},
    {"name": "Mass General Brigham", "careers_url": "https://massgeneralbrigham.org/careers"},
    {"name": "NewYork-Presbyterian", "careers_url": "https://careers.nyp.org"},
    {"name": "Mount Sinai Health System", "careers_url": "https://mountsinai.org/careers"},
    {"name": "NYU Langone Health", "careers_url": "https://nyulangone.org/careers"},
    {"name": "Stanford Health Care", "careers_url": "https://stanfordhealthcare.org/careers"},
    {"name": "UCSF Health", "careers_url": "https://ucsfhealth.org/careers"},
    {"name": "UCLA Health", "careers_url": "https://careers.uclahealth.org"},
    {"name": "Northwestern Medicine", "careers_url": "https://nm.org/careers"},
    {"name": "Duke Health", "careers_url": "https://careers.dukehealth.org"},
    {"name": "MD Anderson Cancer Center", "careers_url": "https://mdanderson.org/careers"},
    {"name": "Memorial Sloan Kettering", "careers_url": "https://careers.mskcc.org"},
    {"name": "Pfizer", "careers_url": "https://pfizer.com/about/careers"},
    {"name": "Merck & Co", "careers_url": "https://jobs.merck.com"},
    {"name": "Johnson & Johnson", "careers_url": "https://jobs.jnj.com"},
    {"name": "Eli Lilly", "careers_url": "https://careers.lilly.com"},
    {"name": "Bristol Myers Squibb", "careers_url": "https://careers.bms.com"},
    {"name": "AbbVie", "careers_url": "https://careers.abbvie.com"},
    {"name": "Novartis", "careers_url": "https://novartis.com/careers"},
    {"name": "AstraZeneca", "careers_url": "https://careers.astrazeneca.com"},
    {"name": "GSK", "careers_url": "https://gsk.com/en-gb/careers"},
    {"name": "Sanofi", "careers_url": "https://sanofi.com/en/careers"},
    {"name": "Takeda", "careers_url": "https://takeda.com/en-us/careers"},
    {"name": "Amgen", "careers_url": "https://careers.amgen.com"},
    {"name": "Gilead Sciences", "careers_url": "https://gilead.com/careers"},
    {"name": "Genentech (Roche)", "careers_url": "https://careers.roche.com"},
    {"name": "Regeneron", "careers_url": "https://careers.regeneron.com"},
    {"name": "Moderna", "careers_url": "https://modernatx.com/careers"},
    {"name": "Biogen", "careers_url": "https://biogen.com/careers"},
    {"name": "Vertex Pharmaceuticals", "careers_url": "https://vrtx.com/careers"},
    {"name": "IQVIA", "careers_url": "https://jobs.iqvia.com"},
    {"name": "Epic Systems", "careers_url": "https://epic.com/careers"},
    {"name": "Oracle Health (Cerner)", "careers_url": "https://careers.oracle.com"},
    {"name": "athenahealth", "careers_url": "https://athenahealth.com/careers"},
    {"name": "Veeva Systems", "careers_url": "https://careers.veeva.com"},
    {"name": "Komodo Health", "careers_url": "https://komodohealth.com/careers"},
    {"name": "Datavant", "careers_url": "https://datavant.com/careers"},
    {"name": "Tempus AI", "careers_url": "https://tempus.com/careers"},
    {"name": "Flatiron Health", "careers_url": "https://flatiron.com/careers"},
    {"name": "Definitive Healthcare", "careers_url": "https://definitivehc.com/company/careers"},
    {"name": "Inovalon", "careers_url": "https://inovalon.com/company/careers"},
    {"name": "Cotiviti", "careers_url": "https://cotiviti.com/careers"},
    {"name": "Premier Inc", "careers_url": "https://premierinc.com/about/careers"},
    {"name": "Health Catalyst", "careers_url": "https://healthcatalyst.com/careers"},
    {"name": "Arcadia", "careers_url": "https://arcadia.io/careers"},
    {"name": "Evolent Health", "careers_url": "https://evolenthealth.com/about/careers"},
    {"name": "Included Health", "careers_url": "https://includedhealth.com/careers"},
    {"name": "Cityblock Health", "careers_url": "https://cityblock.com/careers"},
    {"name": "Omada Health", "careers_url": "https://omadahealth.com/careers"},
    {"name": "Hinge Health", "careers_url": "https://hingehealth.com/careers"},
    {"name": "Cedar", "careers_url": "https://cedar.com/careers"},
    {"name": "R1 RCM", "careers_url": "https://r1rcm.com/careers"},
    {"name": "Quest Diagnostics", "careers_url": "https://jobs.questdiagnostics.com"},
    {"name": "Labcorp", "careers_url": "https://careers.labcorp.com"},
    {"name": "ZS Associates", "careers_url": "https://zs.com/careers"}
]

# California Companies (250)
california_list = [
    {"name": "Apple", "careers_url": "https://jobs.apple.com"},
    {"name": "Google / Alphabet", "careers_url": "https://careers.google.com"},
    {"name": "Meta", "careers_url": "https://metacareers.com"},
    {"name": "Nvidia", "careers_url": "https://nvidia.com/en-us/about-nvidia/careers"},
    {"name": "Salesforce", "careers_url": "https://salesforce.com/company/careers"},
    {"name": "Adobe", "careers_url": "https://adobe.com/careers.html"},
    {"name": "Cisco Systems", "careers_url": "https://jobs.cisco.com"},
    {"name": "Intel", "careers_url": "https://intel.com/content/www/us/en/jobs"},
    {"name": "Oracle", "careers_url": "https://careers.oracle.com"},
    {"name": "Qualcomm", "careers_url": "https://qualcomm.com/company/careers"},
    {"name": "Advanced Micro Devices (AMD)", "careers_url": "https://amd.com/en/corporate/careers"},
    {"name": "VMware (Broadcom)", "careers_url": "https://broadcom.com/company/careers"},
    {"name": "Intuit", "careers_url": "https://intuit.com/careers"},
    {"name": "ServiceNow", "careers_url": "https://careers.servicenow.com"},
    {"name": "Workday", "careers_url": "https://workday.com/en-us/company/careers.html"},
    {"name": "Autodesk", "careers_url": "https://autodesk.com/careers"},
    {"name": "Synopsys", "careers_url": "https://synopsys.com/careers.html"},
    {"name": "Cadence Design Systems", "careers_url": "https://cadence.com/en_US/home/careers.html"},
    {"name": "Applied Materials", "careers_url": "https://careers.appliedmaterials.com"},
    {"name": "Lam Research", "careers_url": "https://lamresearch.com/careers"},
    {"name": "Western Digital", "careers_url": "https://jobs.westerndigital.com"},
    {"name": "Seagate Technology", "careers_url": "https://seagate.com/careers"},
    {"name": "Hewlett Packard Enterprise", "careers_url": "https://hpe.com/us/en/living-progress/careers"},
    {"name": "HP Inc", "careers_url": "https://jobs.hp.com"},
    {"name": "Dell Technologies (CA ops)", "careers_url": "https://dell.com/en-us/dt/corporate/careers"},
    {"name": "NetApp", "careers_url": "https://netapp.com/us/careers"},
    {"name": "Pure Storage", "careers_url": "https://purestorage.com/company/careers.html"},
    {"name": "Palo Alto Networks", "careers_url": "https://paloaltonetworks.com/company/careers"},
    {"name": "Fortinet", "careers_url": "https://fortinet.com/corporate/careers"},
    {"name": "Zscaler", "careers_url": "https://zscaler.com/careers"},
    {"name": "CrowdStrike", "careers_url": "https://crowdstrike.com/careers"},
    {"name": "Splunk (Cisco)", "careers_url": "https://splunk.com/en_us/careers.html"},
    {"name": "Twilio", "careers_url": "https://twilio.com/en-us/company/jobs"},
    {"name": "Okta", "careers_url": "https://okta.com/company/careers"},
    {"name": "DocuSign", "careers_url": "https://careers.docusign.com"},
    {"name": "Zoom", "careers_url": "https://careers.zoom.us"},
    {"name": "Dropbox", "careers_url": "https://dropbox.com/jobs"},
    {"name": "Box", "careers_url": "https://box.com/careers"},
    {"name": "Roku", "careers_url": "https://roku.com/careers"},
    {"name": "Logitech", "careers_url": "https://logitech.com/en-us/careers"},
    {"name": "OpenAI", "careers_url": "https://openai.com/careers"},
    {"name": "Anthropic", "careers_url": "https://anthropic.com/careers"},
    {"name": "Scale AI", "careers_url": "https://scale.com/careers"},
    {"name": "Databricks", "careers_url": "https://databricks.com/company/careers"},
    {"name": "Snowflake", "careers_url": "https://careers.snowflake.com"},
    {"name": "Stripe", "careers_url": "https://stripe.com/jobs"},
    {"name": "Airbnb", "careers_url": "https://careers.airbnb.com"},
    {"name": "Uber", "careers_url": "https://uber.com/us/en/careers"},
    {"name": "Lyft", "careers_url": "https://lyft.com/careers"},
    {"name": "DoorDash", "careers_url": "https://doordash.com/careers"},
    {"name": "Instacart", "careers_url": "https://instacart.careers"},
    {"name": "Pinterest", "careers_url": "https://pinterest.com/careers"},
    {"name": "Reddit", "careers_url": "https://redditinc.com/careers"},
    {"name": "Snap Inc", "careers_url": "https://snap.com/en-US/jobs"},
    {"name": "Robinhood", "careers_url": "https://careers.robinhood.com"},
    {"name": "Coinbase", "careers_url": "https://coinbase.com/careers"},
    {"name": "Plaid", "careers_url": "https://plaid.com/careers"},
    {"name": "Affirm", "careers_url": "https://affirm.com/careers"},
    {"name": "Chime", "careers_url": "https://chime.com/careers"},
    {"name": "Brex", "careers_url": "https://brex.com/careers"},
    {"name": "Ramp", "careers_url": "https://ramp.com/careers"},
    {"name": "Gusto", "careers_url": "https://gusto.com/company/jobs"},
    {"name": "Rippling", "careers_url": "https://rippling.com/careers"},
    {"name": "Notion", "careers_url": "https://notion.so/careers"},
    {"name": "Figma", "careers_url": "https://figma.com/careers"},
    {"name": "Canva (US ops)", "careers_url": "https://canva.com/careers"},
    {"name": "Miro (US ops)", "careers_url": "https://miro.com/careers"},
    {"name": "Asana", "careers_url": "https://asana.com/jobs"},
    {"name": "Riot Games", "careers_url": "https://riotgames.com/en/work-with-us"},
    {"name": "Electronic Arts (EA)", "careers_url": "https://ea.com/careers"},
    {"name": "Activision Blizzard", "careers_url": "https://activisionblizzard.com/careers"},
    {"name": "Unity Technologies", "careers_url": "https://unity.com/careers"},
    {"name": "Discord", "careers_url": "https://discord.com/careers"},
    {"name": "Roblox", "careers_url": "https://careers.roblox.com"},
    {"name": "Niantic", "careers_url": "https://nianticlabs.com/careers"},
    {"name": "Samsara", "careers_url": "https://samsara.com/company/careers"},
    {"name": "Verkada", "careers_url": "https://verkada.com/careers"},
    {"name": "GitLab (US remote)", "careers_url": "https://about.gitlab.com/jobs"},
    {"name": "HashiCorp (IBM)", "careers_url": "https://hashicorp.com/careers"},
    {"name": "Confluent", "careers_url": "https://confluent.io/careers"},
    {"name": "Anyscale", "careers_url": "https://anyscale.com/careers"},
    {"name": "Cohere (US ops)", "careers_url": "https://cohere.com/careers"},
    {"name": "Glean", "careers_url": "https://glean.com/careers"},
    {"name": "Perplexity AI", "careers_url": "https://perplexity.ai/careers"},
    {"name": "Character.AI", "careers_url": "https://character.ai/careers"},
    {"name": "Genentech (Roche)", "careers_url": "https://careers.roche.com"},
    {"name": "Amgen", "careers_url": "https://careers.amgen.com"},
    {"name": "Gilead Sciences", "careers_url": "https://gilead.com/careers"},
    {"name": "AbbVie (Bay Area ops)", "careers_url": "https://careers.abbvie.com"},
    {"name": "Illumina", "careers_url": "https://illumina.com/company/careers.html"},
    {"name": "Bio-Rad Laboratories", "careers_url": "https://bio-rad.com/careers"},
    {"name": "Thermo Fisher (CA ops)", "careers_url": "https://jobs.thermofisher.com"},
    {"name": "Exact Sciences (CA ops)", "careers_url": "https://exactsciences.com/careers"},
    {"name": "Guardant Health", "careers_url": "https://guardanthealth.com/careers"},
    {"name": "Natera", "careers_url": "https://natera.com/careers"},
    {"name": "10x Genomics", "careers_url": "https://10xgenomics.com/careers"},
    {"name": "BioMarin Pharmaceutical", "careers_url": "https://biomarin.com/careers"},
    {"name": "Exelixis", "careers_url": "https://exelixis.com/careers"},
    {"name": "Vir Biotechnology", "careers_url": "https://vir.bio/careers"},
    {"name": "Coherus BioSciences", "careers_url": "https://coherus.com/careers"},
    {"name": "Denali Therapeutics", "careers_url": "https://denalitherapeutics.com/careers"},
    {"name": "Nurix Therapeutics", "careers_url": "https://nurixtx.com/careers"},
    {"name": "Allakos", "careers_url": "https://allakos.com/careers"},
    {"name": "CytomX Therapeutics", "careers_url": "https://cytomx.com/careers"},
    {"name": "Arcus Biosciences", "careers_url": "https://arcusbio.com/careers"},
    {"name": "Revolution Medicines", "careers_url": "https://revmed.com/careers"},
    {"name": "Sutro Biopharma", "careers_url": "https://sutrobio.com/careers"},
    {"name": "Twist Bioscience", "careers_url": "https://twistbioscience.com/careers"},
    {"name": "Zymergen (Ginkgo)", "careers_url": "https://ginkgobioworks.com/careers"},
    {"name": "Grail", "careers_url": "https://grail.com/careers"},
    {"name": "Freenome", "careers_url": "https://freenome.com/careers"},
    {"name": "Cepheid (Danaher)", "careers_url": "https://cepheid.com/en-US/about-us/careers"},
    {"name": "Penumbra", "careers_url": "https://penumbrainc.com/careers"},
    {"name": "Intuitive Surgical", "careers_url": "https://intuitive.com/en-us/about-us/careers"},
    {"name": "Masimo", "careers_url": "https://masimo.com/company/careers"},
    {"name": "Edwards Lifesciences", "careers_url": "https://edwards.com/careers"},
    {"name": "Abbott (CA ops)", "careers_url": "https://abbott.com/careers.html"},
    {"name": "Dexcom", "careers_url": "https://dexcom.com/careers"},
    {"name": "ResMed", "careers_url": "https://resmed.com/en-us/careers"},
    {"name": "Bristol Myers Squibb (CA ops)", "careers_url": "https://careers.bms.com"},
    {"name": "Pfizer (La Jolla ops)", "careers_url": "https://pfizer.com/about/careers"},
    {"name": "Johnson & Johnson (CA ops)", "careers_url": "https://jobs.jnj.com"},
    {"name": "Takeda (CA ops)", "careers_url": "https://takeda.com/en-us/careers"},
    {"name": "Novartis (CA ops)", "careers_url": "https://novartis.com/careers"},
    {"name": "Halozyme Therapeutics", "careers_url": "https://halozyme.com/careers"},
    {"name": "Ionis Pharmaceuticals", "careers_url": "https://ionispharma.com/careers"},
    {"name": "Acadia Pharmaceuticals", "careers_url": "https://acadia-pharm.com/careers"},
    {"name": "Neurocrine Biosciences", "careers_url": "https://neurocrine.com/careers"},
    {"name": "Crinetics Pharmaceuticals", "careers_url": "https://crinetics.com/careers"},
    {"name": "Fate Therapeutics", "careers_url": "https://fatetherapeutics.com/careers"},
    {"name": "Kaiser Permanente (CA)", "careers_url": "https://jobs.kaiserpermanente.org"},
    {"name": "Stanford Health Care (CA)", "careers_url": "https://stanfordhealthcare.org/careers"},
    {"name": "UCSF Health (CA)", "careers_url": "https://ucsfhealth.org/careers"},
    {"name": "UCLA Health (CA)", "careers_url": "https://careers.uclahealth.org"},
    {"name": "UC San Diego Health (CA)", "careers_url": "https://jobs.ucsd.edu"},
    {"name": "Cedars-Sinai (CA)", "careers_url": "https://cedars-sinai.org/careers"},
    {"name": "Sutter Health (CA)", "careers_url": "https://sutterhealth.org/careers"},
    {"name": "Dignity Health (CommonSpirit) (CA)", "careers_url": "https://commonspirit.careers"},
    {"name": "Scripps Health (CA)", "careers_url": "https://scripps.org/careers"},
    {"name": "Sharp HealthCare (CA)", "careers_url": "https://sharp.com/careers"},
    {"name": "Providence (CA)", "careers_url": "https://providence.jobs"},
    {"name": "City of Hope (CA)", "careers_url": "https://cityofhope.org/careers"},
    {"name": "Stanford University (CA)", "careers_url": "https://careers.stanford.edu"},
    {"name": "UC Berkeley (CA)", "careers_url": "https://careerspubs.berkeley.edu"},
    {"name": "Caltech (CA)", "careers_url": "https://caltech.edu/about/careers"},
    {"name": "UC San Diego (CA)", "careers_url": "https://jobs.ucsd.edu"},
    {"name": "UCLA (CA)", "careers_url": "https://careers.ucla.edu"},
    {"name": "USC (CA)", "careers_url": "https://usccareers.usc.edu"},
    {"name": "UC Irvine (CA)", "careers_url": "https://careers.uci.edu"},
    {"name": "UC Davis (CA)", "careers_url": "https://careers.ucdavis.edu"},
    {"name": "Lawrence Livermore National Lab (CA)", "careers_url": "https://llnl.gov/join-our-team"},
    {"name": "Lawrence Berkeley National Lab (CA)", "careers_url": "https://lbl.gov/careers"},
    {"name": "SLAC (Stanford) (CA)", "careers_url": "https://slac.stanford.edu/careers"},
    {"name": "JPL / NASA (Caltech) (CA)", "careers_url": "https://jpl.nasa.gov/careers"},
    {"name": "Blue Shield of California (CA)", "careers_url": "https://blueshieldca.com/careers"},
    {"name": "Health Net (Centene) (CA)", "careers_url": "https://careers.centene.com"},
    {"name": "Molina Healthcare (CA)", "careers_url": "https://careers.molinahealthcare.com"},
    {"name": "SCAN Health Plan (CA)", "careers_url": "https://scanhealthplan.com/careers"},
    {"name": "Alignment Health (CA)", "careers_url": "https://alignmenthealth.com/careers"},
    {"name": "Clover Health (CA)", "careers_url": "https://cloverhealth.com/careers"},
    {"name": "Grand Rounds / Included Health (CA)", "careers_url": "https://includedhealth.com/careers"},
    {"name": "Omada Health (CA)", "careers_url": "https://omadahealth.com/careers"},
    {"name": "Hims & Hers Health (CA)", "careers_url": "https://forhims.com/careers"},
    {"name": "Color Health (CA)", "careers_url": "https://color.com/careers"},
    {"name": "Verily (Alphabet) (CA)", "careers_url": "https://verily.com/careers"},
    {"name": "Devoted Health (CA)", "careers_url": "https://devoted.com/careers"},
    {"name": "Cricket Health / Strive (CA)", "careers_url": "https://strivehealth.com/careers"},
    {"name": "Carbon Health (CA)", "careers_url": "https://carbonhealth.com/careers"},
    {"name": "Forward Health (CA)", "careers_url": "https://goforward.com/careers"},
    {"name": "Cedar (CA)", "careers_url": "https://cedar.com/careers"},
    {"name": "Collective Health (CA)", "careers_url": "https://collectivehealth.com/careers"},
    {"name": "Komodo Health (CA)", "careers_url": "https://komodohealth.com/careers"},
    {"name": "Cohere Health (CA)", "careers_url": "https://coherehealth.com/careers"},
    {"name": "Notable Health (CA)", "careers_url": "https://notablehealth.com/careers"},
    {"name": "Tempus (CA)", "careers_url": "https://tempus.com/careers"},
    {"name": "Visa (CA)", "careers_url": "https://careers.visa.com"},
    {"name": "PayPal (CA)", "careers_url": "https://paypal.com/us/jobs"},
    {"name": "Block (Square) (CA)", "careers_url": "https://block.xyz/careers"},
    {"name": "Charles Schwab (SF ops) (CA)", "careers_url": "https://schwab.com/careers"},
    {"name": "Wells Fargo (SF HQ) (CA)", "careers_url": "https://wellsfargojobs.com"},
    {"name": "First Republic (JPMorgan) (CA)", "careers_url": "https://jpmorgan.com/careers"},
    {"name": "SoFi (CA)", "careers_url": "https://sofi.com/careers"},
    {"name": "Upstart (CA)", "careers_url": "https://upstart.com/careers"},
    {"name": "Marqeta (CA)", "careers_url": "https://marqeta.com/company/careers"},
    {"name": "Bill.com (CA)", "careers_url": "https://bill.com/careers"},
    {"name": "Netflix (CA)", "careers_url": "https://jobs.netflix.com"},
    {"name": "Walt Disney Company (CA)", "careers_url": "https://jobs.disneycareers.com"},
    {"name": "Warner Bros Discovery (CA) (CA ops)", "careers_url": "https://careers.wbd.com"},
    {"name": "Sony Pictures / Sony Interactive (CA)", "careers_url": "https://sonypictures.com/corp/careers"},
    {"name": "Universal Music Group (CA)", "careers_url": "https://universalmusic.com/careers"},
    {"name": "TikTok (CA ops) (CA)", "careers_url": "https://careers.tiktok.com"},
    {"name": "Tesla (CA)", "careers_url": "https://tesla.com/careers"},
    {"name": "Rivian (CA ops) (CA)", "careers_url": "https://rivian.com/careers"},
    {"name": "Lucid Motors (CA)", "careers_url": "https://lucidmotors.com/careers"},
    {"name": "Zoox (Amazon) (CA)", "careers_url": "https://zoox.com/careers"},
    {"name": "Waymo (Alphabet) (CA)", "careers_url": "https://waymo.com/careers"},
    {"name": "Cruise (GM) (CA)", "careers_url": "https://getcruise.com/careers"},
    {"name": "Aurora Innovation (CA ops) (CA)", "careers_url": "https://aurora.tech/careers"},
    {"name": "SpaceX (CA)", "careers_url": "https://spacex.com/careers"},
    {"name": "Northrop Grumman (CA) (CA ops)", "careers_url": "https://northropgrumman.com/careers"},
    {"name": "Lockheed Martin (CA) (CA ops)", "careers_url": "https://lockheedmartin.com/en-us/careers"},
    {"name": "Anduril Industries (CA)", "careers_url": "https://anduril.com/careers"},
    {"name": "Relativity Space (CA)", "careers_url": "https://relativityspace.com/careers"},
    {"name": "Rocket Lab (CA ops) (CA)", "careers_url": "https://rocketlabusa.com/careers"},
    {"name": "Deloitte (CA) (CA ops)", "careers_url": "https://deloitte.com/us/en/careers"},
    {"name": "Accenture (CA) (CA ops)", "careers_url": "https://accenture.com/us-en/careers"},
    {"name": "PwC (CA) (CA ops)", "careers_url": "https://pwc.com/us/en/careers"},
    {"name": "EY (CA) (CA ops)", "careers_url": "https://ey.com/en_us/careers"},
    {"name": "KPMG (CA) (CA ops)", "careers_url": "https://kpmg.com/us/en/careers"},
    {"name": "McKinsey (CA) (CA ops)", "careers_url": "https://mckinsey.com/careers"},
    {"name": "Bain & Company (CA) (CA ops)", "careers_url": "https://bain.com/careers"},
    {"name": "BCG (CA) (CA ops)", "careers_url": "https://careers.bcg.com"},
    {"name": "Slalom (CA) (CA ops)", "careers_url": "https://slalom.com/careers"},
    {"name": "Infosys (CA) (CA ops)", "careers_url": "https://infosys.com/careers"},
    {"name": "Cognizant (CA) (CA ops)", "careers_url": "https://careers.cognizant.com"},
    {"name": "Wipro (CA) (CA ops)", "careers_url": "https://wipro.com/careers"},
    {"name": "TCS (CA) (CA ops)", "careers_url": "https://tcs.com/careers"},
    {"name": "Chevron (CA)", "careers_url": "https://chevron.com/careers"},
    {"name": "Pacific Gas & Electric (PG&E) (CA)", "careers_url": "https://pge.com/careers"},
    {"name": "Southern California Edison (CA)", "careers_url": "https://edison.com/careers"},
    {"name": "Sempra Energy (CA)", "careers_url": "https://sempra.com/careers"},
    {"name": "Bloom Energy (CA)", "careers_url": "https://bloomenergy.com/careers"},
    {"name": "Sunrun (CA)", "careers_url": "https://sunrun.com/careers"},
    {"name": "Gap Inc (CA)", "careers_url": "https://gapinc.com/en-us/careers"},
    {"name": "Williams-Sonoma (CA)", "careers_url": "https://williams-sonomainc.com/careers"},
    {"name": "Levi Strauss & Co (CA)", "careers_url": "https://levistrauss.com/careers"},
    {"name": "Chipotle (Newport Beach HQ) (CA)", "careers_url": "https://careers.chipotle.com"},
    {"name": "Activision (Santa Monica) (CA)", "careers_url": "https://activisionblizzard.com/careers"},
    {"name": "Edwards Lifesciences (Irvine) (CA)", "careers_url": "https://edwards.com/careers"},
    {"name": "Broadcom (CA)", "careers_url": "https://broadcom.com/company/careers"},
    {"name": "Marvell Technology (CA)", "careers_url": "https://marvell.com/company/careers.html"},
    {"name": "Skyworks Solutions (CA)", "careers_url": "https://skyworksinc.com/careers"},
    {"name": "Maxim / Analog Devices (CA)", "careers_url": "https://analog.com/en/about-adi/careers.html"},
    {"name": "Keysight Technologies (CA)", "careers_url": "https://keysight.com/us/en/careers.html"},
    {"name": "Fluidigm / Standard BioTools (CA)", "careers_url": "https://standardbio.com/careers"},
    {"name": "ServiceTitan (CA)", "careers_url": "https://servicetitan.com/careers"},
    {"name": "Bird Rides (CA)", "careers_url": "https://bird.co/careers"},
    {"name": "Cvent / Hopin (CA ops) (CA)", "careers_url": "https://cvent.com/careers"},
    {"name": "Fastly (CA)", "careers_url": "https://fastly.com/about/careers"},
    {"name": "Cloudflare (CA ops) (CA)", "careers_url": "https://cloudflare.com/careers"},
    {"name": "Nextdoor (CA)", "careers_url": "https://nextdoor.com/careers"},
    {"name": "Thumbtack (CA)", "careers_url": "https://thumbtack.com/careers"},
    {"name": "Turo (CA)", "careers_url": "https://turo.com/careers"},
    {"name": "Postmates / Uber Eats (CA)", "careers_url": "https://uber.com/us/en/careers"},
    {"name": "Grammarly (SF ops) (CA)", "careers_url": "https://grammarly.com/jobs"},
    {"name": "Webflow (CA)", "careers_url": "https://webflow.com/careers"},
    {"name": "Airtable (CA)", "careers_url": "https://airtable.com/careers"},
    {"name": "Amplitude (CA)", "careers_url": "https://amplitude.com/careers"},
    {"name": "Segment (Twilio) (CA)", "careers_url": "https://twilio.com/en-us/company/jobs"},
    {"name": "Gusto / Checkr / Lattice (SF startups) (CA)", "careers_url": "https://checkr.com/careers"}
]

# Combine both lists and remove duplicates
combined_list = []
seen_names = set()

# Process healthcare list
for item in healthcare_list:
    name_key = item["name"].strip().lower()
    if name_key not in seen_names:
        seen_names.add(name_key)
        combined_list.append(item)

# Process california list
for item in california_list:
    name_key = item["name"].strip().lower()
    if name_key not in seen_names:
        seen_names.add(name_key)
        combined_list.append(item)

def add_companies():
    print("Connecting to database...")
    db = SessionLocal()
    
    try:
        # Fetch existing names/URLs in DB
        existing_names = {c.name.lower() for c in db.query(Company).all()}
        existing_urls = {c.careers_url.lower() for c in db.query(Company).all() if c.careers_url}
        
        added_count = 0
        skipped_count = 0
        
        for comp in combined_list:
            name = comp["name"].strip()
            url = comp["careers_url"].strip()
            
            # Duplicate check
            if name.lower() in existing_names or url.lower() in existing_urls:
                # print(f"Skipping: {name}")
                skipped_count += 1
                continue
            
            company = Company(
                name=name,
                ats="playwright",
                careers_url=url
            )
            db.add(company)
            
            existing_names.add(name.lower())
            existing_urls.add(url.lower())
            added_count += 1
            print(f"Adding: {name} ({url})")
            
        if added_count > 0:
            db.commit()
            print(f"\nSuccessfully added {added_count} new bulk companies to the database.")
        else:
            print("\nNo new companies added.")
            
        print(f"Summary: {added_count} added, {skipped_count} skipped.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    add_companies()
