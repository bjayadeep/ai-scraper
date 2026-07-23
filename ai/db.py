import os
import bcrypt
import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Use SQLite fallback if DATABASE_URL is not set, but notify user
    DATABASE_URL = "sqlite:///./cyberjobs.db"

# Neon/PostgreSQL connection strings often use the postgres:// prefix.
# SQLAlchemy requires postgresql:// instead of postgres://, so we replace it if present.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Setup SQLAlchemy engine and session
# For SQLite, we need to allow multithreading, but PostgreSQL doesn't need it
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL configuration
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing helpers using bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="editor")  # "admin" or "editor"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    ats = Column(String(50), nullable=False)  # "greenhouse", "lever", "ashby", "playwright"
    token = Column(String(255), index=True, nullable=True)
    careers_url = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    experience_metadata = Column(Text, nullable=True)
    apply_link = Column(Text, unique=True, index=True, nullable=False)
    date_posted = Column(String(50), nullable=True)  # Format: "YYYY-MM-DD"
    scraped_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    source_posted_at = Column(DateTime(timezone=True), nullable=True)
    source_updated_at = Column(DateTime(timezone=True), nullable=True)
    first_seen_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_seen_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    profile_matches = relationship("JobProfileMatch", back_populates="job", cascade="all, delete-orphan")


class JobProfile(Base):
    __tablename__ = "job_profiles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    window_type = Column(String(50), nullable=False)
    timezone = Column(String(100), nullable=False, default="America/New_York")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    job_matches = relationship("JobProfileMatch", back_populates="profile", cascade="all, delete-orphan")


class JobProfileMatch(Base):
    __tablename__ = "job_profile_matches"
    __table_args__ = (UniqueConstraint("job_id", "profile_id", name="uq_job_profile_match"),)

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("job_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    classification_reason = Column(Text, nullable=True)
    matched_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    job = relationship("Job", back_populates="profile_matches")
    profile = relationship("JobProfile", back_populates="job_matches")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)  # e.g., "LOGIN", "COMPANY_ADD", "SCRAPE_RUN"
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="logs")

class Setting(Base):
    __tablename__ = "settings"
    
    key = Column(String(255), primary_key=True, index=True)
    value = Column(Text, nullable=True)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database schemas and seed default user
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Check if a user table is empty, and seed the default admin
    db = SessionLocal()
    try:
        from src.profiles import seed_job_profiles
        seed_job_profiles(db)
        admin_email = os.getenv("ADMIN_EMAIL", "admin@cyberjobs.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "adminpassword123")
        
        # Verify if any user exists
        exists = db.query(User).filter(User.role == "admin").first()
        if not exists:
            hashed = hash_password(admin_password)
            default_admin = User(
                email=admin_email,
                password_hash=hashed,
                role="admin"
            )
            db.add(default_admin)
            db.commit()
            print(f"[DB INIT] Seeded default admin account: {admin_email}")
    except Exception as e:
        print(f"[DB INIT] Seeding failed/skipped: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("[DB INIT] Setting up database tables...")
    init_db()
    print("[DB INIT] Finished.")
