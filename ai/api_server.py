import os
import sys
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
import jwt

# Add current dir to path to resolve local imports
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from db import SessionLocal, User, Company, Job, ActivityLog, get_db, hash_password, verify_password, init_db
from scrape_trigger import scrape_single_company
from config import settings

# Load environmental variables
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey123!@#")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# OAuth2 settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app = FastAPI(title="Cyber Security Job Aggregator API", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB setup
@app.on_event("startup")
def on_startup():
    init_db()

# --- Pydantic Schemas ---
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "editor"  # "admin" or "editor"

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class CompanyCreate(BaseModel):
    name: str
    ats: str  # "greenhouse", "lever", "ashby", "playwright"
    token: Optional[str] = None
    careers_url: Optional[str] = ""

class CompanyResponse(BaseModel):
    id: int
    name: str
    ats: str
    token: Optional[str]
    careers_url: Optional[str]
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class JobResponse(BaseModel):
    id: int
    company: str
    title: str
    location: Optional[str]
    experience_metadata: Optional[str]
    apply_link: str
    date_posted: Optional[str]
    scraped_at: datetime.datetime

    class Config:
        orm_mode = True

class ActivityLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    details: Optional[str]
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class SettingsUpdate(BaseModel):
    min_experience: int
    max_experience: int
    use_ai_filter: bool
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    email_to: str
    email_from: str
    gemini_api_key: Optional[str] = ""
    claude_api_key: Optional[str] = ""


# --- Security / JWT Helpers ---
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    return current_user


# --- ROUTERS ---
router = APIRouter()

# 1. Auth Endpoints
@router.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    token = create_access_token(data={"sub": user.email, "role": user.role})
    
    # Log login activity
    log = ActivityLog(user_id=user.id, action="LOGIN", details=f"User {user.email} successfully logged in.")
    db.add(log)
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email
    }

@router.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at
    }


# 2. Dashboard Endpoints
@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_companies = db.query(Company).count()
    total_jobs = db.query(Job).count()
    
    # Jobs scraped today (UTC)
    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    jobs_today = db.query(Job).filter(Job.scraped_at >= today_start).count()
    
    # Active ATS scrapers count
    ats_breakdown = db.query(Company.ats, func.count(Company.id)).group_by(Company.ats).all()
    ats_stats = {ats: count for ats, count in ats_breakdown}
    
    # Recent activity logs (limit 6)
    recent_logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(6).all()
    logs_data = [
        {
            "id": l.id,
            "action": l.action,
            "details": l.details,
            "created_at": l.created_at,
            "user_email": db.query(User.email).filter(User.id == l.user_id).scalar() if l.user_id else "System"
        }
        for l in recent_logs
    ]
    
    # Scraped jobs trends (last 7 days)
    trends = []
    for i in range(6, -1, -1):
        day = datetime.datetime.utcnow().date() - datetime.timedelta(days=i)
        day_start = datetime.datetime.combine(day, datetime.time.min)
        day_end = datetime.datetime.combine(day, datetime.time.max)
        count = db.query(Job).filter(Job.scraped_at >= day_start, Job.scraped_at <= day_end).count()
        trends.append({
            "date": day.strftime("%b %d"),
            "jobs": count
        })
        
    return {
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "jobs_today": jobs_today,
        "ats_stats": ats_stats,
        "recent_activity": logs_data,
        "trends": trends
    }


# 3. Company Management Endpoints
@router.get("/companies")
def get_companies(
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    search: Optional[str] = Query(None),
    ats: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Company)
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%") | Company.token.ilike(f"%{search}%"))
    if ats:
        query = query.filter(Company.ats == ats.lower())
        
    total = query.count()
    companies = query.order_by(Company.name.asc()).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": companies
    }

@router.post("/companies", response_model=CompanyResponse)
def create_company(req: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Duplicate checks
    existing_name = db.query(Company).filter(Company.name.ilike(req.name)).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="Company with this name already exists.")
        
    if req.token:
        existing_token = db.query(Company).filter(Company.token == req.token.lower()).first()
        if existing_token:
            raise HTTPException(status_code=400, detail="Company with this ATS token already exists.")
            
    company = Company(
        name=req.name.strip(),
        ats=req.ats.strip().lower(),
        token=req.token.strip().lower() if req.token else None,
        careers_url=req.careers_url.strip() if req.careers_url else ""
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    # Log addition
    log = ActivityLog(
        user_id=current_user.id,
        action="COMPANY_ADD",
        details=f"Added company {company.name} ({company.ats})"
    )
    db.add(log)
    db.commit()
    
    return company

@router.put("/companies/{id}", response_model=CompanyResponse)
def update_company(id: int, req: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    # Duplicate checks excluding self
    existing_name = db.query(Company).filter(Company.name.ilike(req.name), Company.id != id).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="Company with this name already exists.")
        
    if req.token:
        existing_token = db.query(Company).filter(Company.token == req.token.lower(), Company.id != id).first()
        if existing_token:
            raise HTTPException(status_code=400, detail="Company with this ATS token already exists.")
            
    old_details = f"{company.name} ({company.ats})"
    company.name = req.name.strip()
    company.ats = req.ats.strip().lower()
    company.token = req.token.strip().lower() if req.token else None
    company.careers_url = req.careers_url.strip() if req.careers_url else ""
    
    db.commit()
    db.refresh(company)
    
    # Log edit
    log = ActivityLog(
        user_id=current_user.id,
        action="COMPANY_EDIT",
        details=f"Edited company ID {id}: changed {old_details} to {company.name} ({company.ats})"
    )
    db.add(log)
    db.commit()
    
    return company

@router.delete("/companies/{id}")
def delete_company(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    company_name = company.name
    db.delete(company)
    db.commit()
    
    # Log deletion
    log = ActivityLog(
        user_id=current_user.id,
        action="COMPANY_DELETE",
        details=f"Deleted company {company_name}"
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": f"Successfully deleted company {company_name}"}

@router.post("/companies/{id}/scrape")
def trigger_scrape(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = scrape_single_company(id, user_id=current_user.id)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to scrape company"))
    return result


# 4. Jobs Board Endpoints
@router.get("/jobs")
def get_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    search: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Job)
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%") | Job.location.ilike(f"%{search}%") | Job.company.ilike(f"%{search}%"))
    if company:
        query = query.filter(Job.company == company)
        
    total = query.count()
    jobs = query.order_by(Job.date_posted.desc(), Job.scraped_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": jobs
    }


# 5. Users Administration Endpoints (Admin Only)
@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(User).order_by(User.email.asc()).all()

@router.post("/users", response_model=UserResponse)
def create_user(req: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
        
    user = User(
        email=req.email.strip(),
        password_hash=hash_password(req.password),
        role=req.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log addition
    log = ActivityLog(
        user_id=current_user.id,
        action="USER_CREATE",
        details=f"Created user account: {user.email} (Role: {user.role})"
    )
    db.add(log)
    db.commit()
    
    return user

@router.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
    user_email = user.email
    db.delete(user)
    db.commit()
    
    # Log deletion
    log = ActivityLog(
        user_id=current_user.id,
        action="USER_DELETE",
        details=f"Deleted user account: {user_email}"
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": f"Successfully deleted user {user_email}"}


# 6. Activity Logs Endpoints
@router.get("/activity")
def get_activity_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ActivityLog)
    if action:
        query = query.filter(ActivityLog.action == action)
        
    total = query.count()
    logs = query.order_by(ActivityLog.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    logs_data = [
        {
            "id": l.id,
            "action": l.action,
            "details": l.details,
            "created_at": l.created_at,
            "user_email": db.query(User.email).filter(User.id == l.user_id).scalar() if l.user_id else "System"
        }
        for l in logs
    ]
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": logs_data
    }


# 7. System Settings Endpoints
@router.get("/settings")
def get_sys_settings(current_user: User = Depends(get_current_user)):
    return {
        "min_experience": int(os.getenv("MIN_EXPERIENCE", settings.EXPERIENCE_MIN_YEARS)),
        "max_experience": int(os.getenv("MAX_EXPERIENCE", settings.EXPERIENCE_MAX_YEARS)),
        "use_ai_filter": os.getenv("USE_AI_FILTER", "false").lower() == "true",
        "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_user": os.getenv("SMTP_USER", ""),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "email_to": os.getenv("EMAIL_TO", ""),
        "email_from": os.getenv("EMAIL_FROM", ""),
        "claude_api_key": os.getenv("CLAUDE_API_KEY", "")
    }

@router.post("/settings")
def update_sys_settings(req: SettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Write settings back to .env file
    env_path = current_dir.parent / ".env"
    
    env_lines = []
    updated_keys = {
        "MIN_EXPERIENCE": str(req.min_experience),
        "MAX_EXPERIENCE": str(req.max_experience),
        "USE_AI_FILTER": "true" if req.use_ai_filter else "false",
        "SMTP_HOST": req.smtp_host,
        "SMTP_PORT": str(req.smtp_port),
        "SMTP_USER": req.smtp_user,
        "SMTP_PASSWORD": req.smtp_password,
        "EMAIL_TO": req.email_to,
        "EMAIL_FROM": req.email_from,
    }
    
    if req.claude_api_key:
        updated_keys["CLAUDE_API_KEY"] = req.claude_api_key
        
    # Read existing settings from .env file
    existing_content = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith("#"):
                    continue
                if "=" in line_stripped:
                    key, val = line_stripped.split("=", 1)
                    existing_content[key.strip()] = val.strip()

    # Merge keys
    existing_content.update(updated_keys)
    
    # Write config back
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            for key, val in existing_content.items():
                f.write(f"{key}={val}\n")
                
        # Re-set OS environment variables
        for key, val in updated_keys.items():
            os.environ[key] = val
            
        # Update setting constants dynamically in settings.py module
        settings.EXPERIENCE_MIN_YEARS = req.min_experience
        settings.EXPERIENCE_MAX_YEARS = req.max_experience
        settings.USE_AI_FILTER = req.use_ai_filter
        
        # Log setting change
        log = ActivityLog(
            user_id=current_user.id,
            action="SETTINGS_CHANGE",
            details=f"Updated scraper criteria: Exp range [{req.min_experience} - {req.max_experience} yrs], AI Filter={req.use_ai_filter}"
        )
        db.add(log)
        db.commit()
        
        return {"success": True, "message": "Settings updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")

# Mount Router
app.include_router(router, prefix="/api")
