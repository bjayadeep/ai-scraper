import os
import bcrypt
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Use SQLite fallback if DATABASE_URL is not set, but notify user
    DATABASE_URL = "sqlite:///./cyberjobs.db"

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

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)  # e.g., "LOGIN", "COMPANY_ADD", "SCRAPE_RUN"
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="logs")

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
