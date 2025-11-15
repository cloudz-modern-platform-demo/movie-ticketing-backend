"""Database session and engine configuration for SQLite."""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Resolve the database file path
DB_DIR = Path(__file__).resolve().parents[4] / "data"
DB_PATH = DB_DIR / "app.db"

# Ensure the data directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

# SQLite connection string
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False,  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    Should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)

