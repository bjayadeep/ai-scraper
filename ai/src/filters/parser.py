import re
import logging
from typing import Dict, Any, Tuple
from config import settings
from src.profiles import matches_profile_title

logger = logging.getLogger(__name__)

# Experience regexes
# Matches: "3-5 years", "3+ years", "minimum of 2 years", "1 to 6 years", "4 yrs", etc.
EXPERIENCE_PATTERNS = [
    re.compile(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years?|yrs?)\b", re.IGNORECASE),
    re.compile(r"(\d+)\s*\+\s*(?:years?|yrs?)\b", re.IGNORECASE),
    re.compile(r"(?:minimum|at least|requried|require)\s*(?:of)?\s*(\d+)\s*(?:years?|yrs?)\b", re.IGNORECASE),
    re.compile(r"(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|relevant)\b", re.IGNORECASE)
]

# Exclusions for senior roles that exceed 6 years
SENIORITY_EXCLUSIONS = [
    r"\bsenior\b", r"\bsr\.\b", r"\bprincipal\b", r"\blead\b", 
    r"\bdirector\b", r"\bmanager\b", r"\bvp\b", r"\bhead\b", r"\bchief\b"
]

def clean_html(html_text: str) -> str:
    """Removes HTML tags from a text block."""
    if not html_text:
        return ""
    clean = re.compile("<.*?>")
    return re.sub(clean, " ", html_text)

def is_usa_location(location: str, description: str = "") -> bool:
    """Checks if the job location is in the United States."""
    if not location:
        # Check description for explicit US mentions if location is missing
        desc_lower = description.lower()
        return "united states" in desc_lower or "remote (us)" in desc_lower or "us-based" in desc_lower

    loc_lower = location.lower()
    
    # Common US location indicators
    us_indicators = [
        "us", "usa", "united states", "america", "remote, us", "remote (us)", "remote - us",
        "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id", "il", "in", "ia",
        "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
        "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt",
        "va", "wa", "wv", "wi", "wy"
    ]
    
    # Check if location matches standard indicators
    # Break into words or parts to avoid matching substrings like "india" matching "in"
    parts = [p.strip(",. ") for p in re.split(r"[\s/]+", loc_lower)]
    
    # Explicit check for international locations that might conflict
    international_exclusions = ["uk", "united kingdom", "canada", "ca (canada)", "india", "in (india)", "germany", "de (germany)", "london", "munich", "berlin", "bangalore"]
    
    if any(ex in loc_lower for ex in international_exclusions):
        # Double check if it's dual-listed or truly international
        if "us" not in parts and "usa" not in parts and "united states" not in loc_lower:
            return False
            
    # Check if parts contain US state codes or country name
    for part in parts:
        if part in ["us", "usa", "united states"]:
            return True
        # For state codes, match exactly as separate token
        if len(part) == 2 and part in us_indicators:
            return True
            
    # Standard string search check
    if any(ind in loc_lower for ind in ["united states", "remote - us", "remote (us)", "remote, us", "united states of america"]):
        return True
        
    return False

def parse_experience(description: str, title: str = "") -> Tuple[bool, str]:
    """
    Parses experience required from the job description.
    Returns:
        Tuple[bool, str]: (is_within_range, extracted_experience_string)
        
    Range: Dynamic based on settings.
    """
    min_exp_limit = settings.EXPERIENCE_MIN_YEARS
    max_exp_limit = settings.EXPERIENCE_MAX_YEARS
    title_lower = title.lower()
    desc_clean = clean_html(description)
    # First heuristic: Check title for seniority level. 
    # If the title is "Senior ...", "Principal ...", "Lead ...", "Director ...", 
    # it is highly likely to require more than max_exp_limit years of experience.
    # However, some companies call 5-6 years "Senior". So we still parse the description,
    # but we flag it if there's no experience text found.
    is_senior_title = any(re.search(pat, title_lower) for pat in SENIORITY_EXCLUSIONS)
    
    # Find all mentions of years of experience in the description
    found_years = []
    experience_mentions = []
    
    for pattern in EXPERIENCE_PATTERNS:
        matches = pattern.findall(desc_clean)
        for match in matches:
            if isinstance(match, tuple):
                # E.g. ("3", "5") or ("3", "")
                val1, val2 = match
                if val1:
                    found_years.append(int(val1))
                    if val2:
                        found_years.append(int(val2))
                        experience_mentions.append(f"{val1}-{val2} years")
                    else:
                        experience_mentions.append(f"{val1}+ years")
            else:
                # E.g. "3"
                if match:
                    found_years.append(int(match))
                    experience_mentions.append(f"{match} years")
                    
    # If we extracted years, let's analyze if they fit within limits
    if found_years:
        max_exp = max(found_years)
        min_exp = min(found_years)
        
        # If the minimum experience required is greater than max_exp_limit, reject
        if min_exp > max_exp_limit:
            return False, f"Requires {min_exp}+ yrs (exceeds {max_exp_limit} yrs)"

        # If the maximum experience required is less than min_exp_limit, reject
        if max_exp < min_exp_limit:
            return False, f"Requires {max_exp} yrs (below {min_exp_limit} yrs)"

        # If the maximum experience requested is greater than (max_exp_limit + 2) and title is senior, reject
        if max_exp > (max_exp_limit + 2) and is_senior_title:
            return False, f"Requires {max_exp} yrs (Senior/Principal)"
            
        return True, ", ".join(experience_mentions[:2])
        
    # Heuristic fallback: If no years of experience mentioned in description
    if is_senior_title:
        # Senior / Principal titles with no exp details might be too senior
        if any(w in title_lower for w in ["principal", "director", "manager", "chief", "head", "vp"]):
            return False, f"Senior leadership role (assumed > {max_exp_limit} yrs)"
        return True, "Assumed mid-level senior"
        
    return True, f"Not specified (Assumed {min_exp_limit}-{max_exp_limit} yrs)"

def filter_job(job: Dict[str, Any], profile: Any) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Applies the full verification pipeline to a single job.
    Returns:
        Tuple[bool, str, Dict[str, Any]]: (is_match, reason, job_with_metadata)
    """
    title = job.get("title", "")
    location = job.get("location", "")
    description = job.get("description", "")
    
    # 1. Location check
    if not is_usa_location(location, description):
        return False, "Not in USA", job
        
    # 2. Selected profile role check
    is_role_match, role_reason = matches_profile_title(title, profile)
    if not is_role_match:
        return False, role_reason, job
        
    # 3. Experience check
    is_exp_match, exp_reason = parse_experience(description, title)
    if not is_exp_match:
        return False, f"Experience out of range: {exp_reason}", job
        
    # Enrich job dictionary with parsed metadata
    enriched_job = job.copy()
    enriched_job["experience_metadata"] = exp_reason
    
    return True, role_reason, enriched_job
